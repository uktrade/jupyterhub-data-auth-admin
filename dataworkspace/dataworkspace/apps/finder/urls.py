from django.urls import path

from dataworkspace.apps.accounts.utils import login_required
from dataworkspace.apps.finder import views

urlpatterns = [
    path('', login_required(views.find_datasets), name='find_datasets'),
    path(
        "/search-in-data-explorer/{schema:str}/{table:str}",
        login_required(views.search_in_data_explorer),
        name='search_in_data_explorer',
    ),
]
