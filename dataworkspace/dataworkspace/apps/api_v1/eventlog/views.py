from rest_framework import viewsets

from dataworkspace.apps.api_v1.eventlog.serializers import EventLogSerializer
from dataworkspace.apps.api_v1.pagination import TimestampCursorPagination
from dataworkspace.apps.eventlog.models import EventLog


class EventLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint to list EvenLog items for consumption by data flow.
    """

    queryset = EventLog.objects.all()
    serializer_class = EventLogSerializer
    pagination_class = TimestampCursorPagination
