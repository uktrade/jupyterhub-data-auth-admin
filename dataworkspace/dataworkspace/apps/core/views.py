import csv
import logging

import gevent
import gevent.queue

from psycopg2 import connect, sql

from django.conf import settings
from django.http import (HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotAllowed,
                         HttpResponseNotFound, StreamingHttpResponse)
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView

from dataworkspace.apps.core.forms import SupportForm
from dataworkspace.apps.core.utils import can_access_schema_table, database_dsn
from dataworkspace.zendesk import create_support_request

logger = logging.getLogger('app')


def public_error_404_html_view(request, exception=None):
    return render(request, 'error_404.html', status=404)


def public_error_403_html_view(request, exception=None):
    return render(request, 'error_403.html', status=403)


def public_error_500_html_view(request):
    message = request.GET.get('message', None)
    return render(request, 'error_500.html', {'message': message}, status=500)


def healthcheck_view(_):
    return HttpResponse('OK')


class SupportView(FormView):
    form_class = SupportForm
    template_name = 'core/support.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx['ticket_id'] = self.kwargs.get('ticket_id')
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            'email': self.request.user.email,
        }
        return kwargs

    def form_valid(self, form):
        cleaned = form.cleaned_data
        ticket_id = create_support_request(
            self.request.user,
            cleaned['email'],
            cleaned['message'],
            attachments=[cleaned[x] for x in [
                'attachment1', 'attachment2', 'attachment3'
            ] if cleaned[x] is not None]
        )
        return HttpResponseRedirect(
            reverse('support-success', kwargs={'ticket_id': ticket_id})
        )


def table_data_view(request, database, schema, table):
    logger.info('table_data_view attempt: %s %s %s %s',
                request.user.email, database, schema, table)
    response = \
        HttpResponseNotAllowed(['GET']) if request.method != 'GET' else \
        HttpResponseForbidden() if not can_access_schema_table(request.user, database, schema, table) else \
        HttpResponseNotFound() if not _table_exists(database, schema, table) else \
        _table_data(request.user.email, database, schema, table)

    return response


def _table_exists(database, schema, table):
    with \
            connect(database_dsn(settings.DATABASES_DATA[database])) as conn, \
            conn.cursor() as cur:

        cur.execute("""
            SELECT 1
            FROM
                pg_tables
            WHERE
                schemaname = %s
            AND
                tablename = %s
        """, (schema, table))
        return bool(cur.fetchone())


def _table_data(user_email, database, schema, table):
    logger.info('table_data_view start: %s %s %s %s', user_email, database, schema, table)
    cursor_itersize = 1000
    queue_size = 5
    bytes_queue = gevent.queue.Queue(maxsize=queue_size)

    def put_db_rows_to_queue():
        # The csv writer "writes" its output by calling a file-like object
        # with a `write` method.
        class PseudoBuffer:
            def write(self, value):
                return value
        csv_writer = csv.writer(PseudoBuffer())

        with \
                connect(database_dsn(settings.DATABASES_DATA[database])) as conn, \
                conn.cursor(name='all_table_data') as cur:  # Named cursor => server-side cursor

            cur.itersize = cursor_itersize
            cur.arraysize = cursor_itersize

            # There is no ordering here. We just want a full dump.
            # Also, there are not likely to be updates, so a long-running
            # query shouldn't cause problems with concurrency/locking
            cur.execute(sql.SQL("""
                SELECT
                    *
                FROM
                    {}.{}
            """).format(sql.Identifier(schema), sql.Identifier(table)))

            i = 0
            while True:
                rows = cur.fetchmany(cursor_itersize)
                if i == 0:
                    # Column names are not populated until the first row fetched
                    bytes_queue.put(csv_writer.writerow(
                        [column_desc[0] for column_desc in cur.description]), timeout=10)
                bytes_fetched = ''.join(
                    csv_writer.writerow(row) for row in rows
                ).encode('utf-8')
                bytes_queue.put(bytes_fetched, timeout=15)
                i += len(rows)
                if not rows:
                    break

            bytes_queue.put(csv_writer.writerow(['Number of rows: ' + str(i)]))

    def yield_bytes_from_queue():
        while put_db_rows_to_queue_job:
            try:
                # There will be a 0.1 second wait after the end of the data
                # from the db to when the connection is closed. Might be able
                # to avoid this, but KISS, and minor
                yield bytes_queue.get(timeout=0.1)
            except gevent.queue.Empty:
                pass

        logger.info('table_data_view end: %s %s %s %s', user_email, database, schema, table)

    def handle_exception(job):
        try:
            raise job.exception
        except Exception:
            logger.exception('table_data_view exception: %s %s %s %s',
                             user_email, database, schema, table)

    put_db_rows_to_queue_job = gevent.spawn(put_db_rows_to_queue)
    put_db_rows_to_queue_job.link_exception(handle_exception)

    response = StreamingHttpResponse(yield_bytes_from_queue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{schema}_{table}.csv"'
    return response