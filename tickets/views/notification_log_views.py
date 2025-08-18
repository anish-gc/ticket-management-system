"""
This module handles operations related to notification logs including
listing,  retrieving by ID, and deleting notification logs.
Authentication is managed through a custom JWT authentication mechanism.
"""

import logging

from tickets.models.notification_log_model import NotificationLog

from tickets.serializers.notification_log_serializer import (
    NotificationLogReadSerializer,
)
from utilities.api_views import BaseAPIView

logger = logging.getLogger("django")


class NotificationLogsListApiView(BaseAPIView):
    """API endpoint for  listing notification logs."""

    menu_url = "/notification-logs/"

    def get(self, request):
        """Retrieve all notification logs."""
        notifcation_logs = self.get_serializer_data(
            NotificationLog, NotificationLogReadSerializer,  self.request,  True, True, **{'is_active': True}
        )

        tickets_data = self.get_menu_tickets()
        return self.handle_success({
            "notifcationData": notifcation_logs,
            "ticketsData": tickets_data
        })
        return self.handle_serializer_data(
            NotificationLog, NotificationLogReadSerializer, True
        )


class NotificationLogDetailsApiView(BaseAPIView):
    """API endpoint for retrieving and deleting a specific notification log."""

    menu_url = "/notification-logs/"

    def get(self, request, pk):
        """Retrieve a notification log by reference_id."""
        return self.handle_serializer_data(
            NotificationLog, NotificationLogReadSerializer, False, reference_id=pk
        )

    def delete(self, request, pk):
        """Delete a notification log."""
        try:
            log = NotificationLog.objects.get(reference_id=pk)
            log.delete()
            return self.handle_success("Notfication Log deleted successfully.")

        except Exception as exe:
            return self.handle_view_exception(exe)
