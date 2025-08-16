"""
This module handles operations related to tickets including listing, creating, updating, retrieving by ID, and deleting ticket.
Authentication is managed through a custom JWT authentication mechanism.
"""

import logging
from datetime import datetime

from tickets.models.ticket_model import Ticket
from tickets.serializers.ticket_serializer import TicketListSerializer, TicketSerializer
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException

logger = logging.getLogger("django")


class TicketCreateListApiView(BaseAPIView):
    """API endpoint for creating and listing tickets."""

    menu_url = "/tickets/"

    def get(self, request):
        """Retrieve all tickets."""
        return self.handle_serializer_data(Ticket, TicketListSerializer, True)

    def post(self, request):
        """Create a new ticket."""
        serializer = TicketSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(created_by=request.user, created_at=datetime.now())
            return self.handle_success("Ticket created successfully.")
        return self.handle_invalid_serializer(serializer)


class TicketDetailsApiView(BaseAPIView):
    """API endpoint for retrieving, updating, and deleting a specific ticket."""

    menu_url = "/tickets/"

    def get(self, request, pk):
        """Retrieve a ticket by reference_id."""
        return self.handle_serializer_data(
            Ticket, TicketListSerializer, False, reference_id=pk
        )

    def patch(self, request, pk):
        """Update a ticket."""
        ticket = Ticket.objects.get(reference_id=pk)

        serializer = TicketSerializer(
            ticket, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return self.handle_success("Ticket updated successfully.")
        return self.handle_invalid_serializer(serializer)

    def delete(self, request, pk):
        """Delete a ticket."""
        try:
            ticket = Ticket.objects.get(reference_id=pk)
            ticket.delete()
            return self.handle_success("Ticket deleted successfully.")
        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)
        except Exception as exe:
            return self.handle_view_exception(exe)      
