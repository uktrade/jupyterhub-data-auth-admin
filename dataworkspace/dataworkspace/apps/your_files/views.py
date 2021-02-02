from csp.decorators import csp_update
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView
from requests import HTTPError

from waffle.mixins import WaffleFlagMixin

from dataworkspace.apps.core.utils import (
    USER_SCHEMA_STEM,
    db_role_schema_suffix_for_user,
    get_s3_prefix,
)
from dataworkspace.apps.your_files.forms import CreateTableForm
from dataworkspace.apps.your_files.utils import (
    copy_file_to_uploads_bucket,
    get_s3_csv_column_types,
    clean_db_identifier,
    trigger_dataflow_dag,
)


def file_browser_html_view(request):
    return (
        file_browser_html_GET(request)
        if request.method == 'GET'
        else HttpResponse(status=405)
    )


@csp_update(
    CONNECT_SRC=[settings.APPLICATION_ROOT_DOMAIN, "https://s3.eu-west-2.amazonaws.com"]
)
def file_browser_html_GET(request):
    prefix = get_s3_prefix(str(request.user.profile.sso_id))

    return render(
        request,
        'files.html',
        {
            'prefix': prefix,
            'bucket': settings.NOTEBOOKS_BUCKET,
            'YOUR_FILES_CREATE_TABLE_FLAG': settings.YOUR_FILES_CREATE_TABLE_FLAG,
        },
        status=200,
    )


class CreateTableView(WaffleFlagMixin, FormView):
    waffle_flag = settings.YOUR_FILES_CREATE_TABLE_FLAG
    form_class = CreateTableForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        path = form.cleaned_data['path']
        schema = (
            f'{USER_SCHEMA_STEM}{db_role_schema_suffix_for_user(self.request.user)}'
        )
        table_name = clean_db_identifier(path)
        column_definitions = get_s3_csv_column_types(path)
        import_path = settings.DATAFLOW_IMPORTS_BUCKET_ROOT + '/' + path
        copy_file_to_uploads_bucket(path, import_path)
        try:
            trigger_dataflow_dag(import_path, schema, table_name, column_definitions)
        except HTTPError:
            return self.form_invalid(form)
        messages.success(self.request, 'Table created')
        return HttpResponseRedirect(reverse('your-files:files'))

    def form_invalid(self, form):
        messages.error(self.request, 'An error occurred while processing your file')
        return HttpResponseRedirect(reverse('your-files:files'))