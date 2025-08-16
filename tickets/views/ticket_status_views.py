"""
This module handles operations related to ticket statuses including
listing, creating, updating, retrieving by ID, and deleting ticket statuses.
Authentication is managed through a custom JWT authentication mechanism.
"""

import logging
from datetime import datetime

from tickets.models.ticket_status_model import TicketStatus
from tickets.serializers.ticket_status_serializer import (
    TicketStatusListSerializer,
    TicketStatusSerializer,
)
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException

logger = logging.getLogger("django")


class TicketStatusCreateListApiView(BaseAPIView):
    """API endpoint for creating and listing ticket statuses."""

    menu_url = "/ticket-status/"

    def get(self, request):
        """Retrieve all ticket statuses."""
        return self.handle_serializer_data(TicketStatus, TicketStatusListSerializer, True)

    def post(self, request):
        """Create a new ticket status."""
        serializer = TicketStatusSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(created_by=request.user, created_at=datetime.now())
            return self.handle_success("Ticket status created successfully.")
        return self.handle_invalid_serializer(serializer)


class TicketStatusDetailsApiView(BaseAPIView):
    """API endpoint for retrieving, updating, and deleting a specific ticket status."""

    menu_url = "/ticket-status/"

    def get(self, request, pk):
        """Retrieve a ticket status by reference_id."""
        return self.handle_serializer_data(
            TicketStatus, TicketStatusListSerializer, False, reference_id=pk
        )

    def patch(self, request, pk):
        """Update a ticket status."""
        status = TicketStatus.objects.get(reference_id=pk)

        serializer = TicketStatusSerializer(
            status, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return self.handle_success("Ticket status updated successfully.")
        return self.handle_invalid_serializer(serializer)

    def delete(self, request, pk):
        """Delete a ticket status."""
        try:
            status = TicketStatus.objects.get(reference_id=pk)
            status.delete()
            return self.handle_success("Ticket status deleted successfully.")
        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)
        except Exception as exe:
            return self.handle_view_exception(exe)
