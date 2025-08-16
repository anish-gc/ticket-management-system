"""
This module handles operations related to ticket priorities including
listing, creating, updating, retrieving by ID, and deleting ticket priorities.
Authentication is managed through a custom JWT authentication mechanism.
"""

import logging
from datetime import datetime

from tickets.models.ticket_priority_model import TicketPriority
from tickets.serializers.ticket_priority_serializer import (
    TicketPriorityListSerializer,
    TicketPrioritySerializer,
)
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException

logger = logging.getLogger("django")


class TicketPriorityCreateListApiView(BaseAPIView):
    """API endpoint for creating and listing ticket priorities."""

    menu_url = "/ticket-priority/"

    def get(self, request):
        """Retrieve all ticket priorities."""
        return self.handle_serializer_data(
            TicketPriority, TicketPriorityListSerializer, True
        )

    def post(self, request):
        """Create a new ticket priority."""
        serializer = TicketPrioritySerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(created_by=request.user, created_at=datetime.now())
            return self.handle_success("Ticket priority created successfully.")
        return self.handle_invalid_serializer(serializer)


class TicketPriorityDetailsApiView(BaseAPIView):
    """API endpoint for retrieving, updating, and deleting a specific ticket priority."""

    menu_url = "/ticket-priority/"

    def get(self, request, pk):
        """Retrieve a ticket priority by reference_id."""
        return self.handle_serializer_data(
            TicketPriority, TicketPriorityListSerializer, False, reference_id=pk
        )

    def patch(self, request, pk):
        """Update a ticket priority."""
        priority = TicketPriority.objects.get(reference_id=pk)

        serializer = TicketPrioritySerializer(
            priority, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return self.handle_success("Ticket priority updated successfully.")
        return self.handle_invalid_serializer(serializer)

    def delete(self, request, pk):
        """Delete a ticket priority."""
        try:
            priority = TicketPriority.objects.get(reference_id=pk)
            priority.delete()
            return self.handle_success("Ticket priority deleted successfully.")
        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)
        except Exception as exe:
            return self.handle_view_exception(exe)
