from datetime import datetime, timedelta

from celery.utils.log import get_task_logger
from django.db import connections
from pytz import utc

from dataworkspace.apps.explorer.models import Query, QueryLog, PlaygroundSQL
from dataworkspace.apps.explorer.utils import materialized_view_name_for_query
from dataworkspace.cel import celery_app


logger = get_task_logger(__name__)


@celery_app.task()
def truncate_querylogs(days):
    qs = QueryLog.objects.filter(run_at__lt=datetime.now() - timedelta(days=days))
    logger.info('Deleting %s QueryLog objects older than %s days.', qs.count, days)
    qs.delete()
    logger.info('Done deleting QueryLog objects.')


@celery_app.task()
def cleanup_playground_sql_table():
    older_than = timedelta(days=14)
    oldest_date_to_retain = datetime.now(tz=utc) - older_than

    logger.info(
        "Cleaning up Data Explorer PlaygroundSQL rows older than %s",
        oldest_date_to_retain,
    )

    count = 0
    for play_sql in PlaygroundSQL.objects.filter(created_at__lte=oldest_date_to_retain):
        play_sql.delete()
        count += 1

    logger.info("Delete %s PlaygroundSQL rows", count)


@celery_app.task()
def cleanup_materialized_views():
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    logger.info(
        "Cleaning up Data Explorer materialized views older than %s", one_day_ago
    )

    for query in Query.objects.filter(last_run_date__lte=one_day_ago):
        with connections[query.connection].cursor() as cursor:
            view_name = materialized_view_name_for_query(query.created_by_user, query)
            logger.info("Dropping view %s", view_name)
            cursor.execute(f'DROP MATERIALIZED VIEW IF EXISTS {view_name}')
