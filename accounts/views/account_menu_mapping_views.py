"""
This module handles operations related to user menu assignments including listing, creating, updating, retrieving by ID, and deleting user menu assignments.
Authentication is managed through a custom JWT authentication mechanism.
"""

import logging
from datetime import datetime

from accounts.models.user_menu_assignment_model import UserMenuAssignment
from accounts.serializers.user_menu_assignment_serializer import (
    UserMenuAssignmentListSerializer,
    UserMenuAssignmentSerializer,
)
from utilities.api_views import BaseAPIView

logger = logging.getLogger("django")


class AccountMenuMappingCreateListApiView(BaseAPIView):
    """API endpoint for creating and listing user menu assignments."""

    menu_url = "/account/menu/mapping/"

    def get(self, request):
        """Retrieve all user menu assignments."""
        user_menu_assignment_data = self.get_serializer_data(
            UserMenuAssignment, 
            UserMenuAssignmentListSerializer, 
            request=self.request,  
            paginate=True,  # Enable pagination
            is_active=True
        )   
        tickets_data = self.get_menu_tickets()
        return self.handle_success({
            "userMenuAssignmentdata": user_menu_assignment_data,
            "ticketsData": tickets_data
        })
       
    def post(self, request):
        """Create a new role."""
        serializer = UserMenuAssignmentSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(
                created_by=request.user,
                created_at=datetime.now(),
                assigned_by=request.user,
            )
            return self.handle_success("UserMenuAssignment created successfully.")
        return self.handle_invalid_serializer(serializer)


class AccountMenuMappingDetailsApiView(BaseAPIView):
    """API endpoint for retrieving, updating, and deleting a specific user menu assignment."""

    menu_url = "/account/menu/mapping/"

    def get(self, request, pk):
        """Retrieve a user menu assignment by reference_id."""
        return self.handle_serializer_data(
            UserMenuAssignment, UserMenuAssignmentListSerializer, False, reference_id=pk
        )

    def patch(self, request, pk):
        """Update a role."""
        user_menu_assignment = UserMenuAssignment.objects.get(reference_id=pk)

        serializer = UserMenuAssignmentSerializer(
            user_menu_assignment,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return self.handle_success("UserMenuAssignment updated successfully.")
        return self.handle_invalid_serializer(serializer)

    def delete(self, request, pk):
        """Delete a user menu assignment."""
        try:
            user_menu_assignment = UserMenuAssignment.objects.get(reference_id=pk)
            user_menu_assignment.delete()
            return self.handle_success("UserMenuAssignment deleted successfully.")

        except Exception as exe:
            return self.handle_view_exception(exe)
