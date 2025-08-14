"""
This module handles operations related to roles including listing, creating, updating, retrieving by ID, and deleting roles.
Authentication is managed through a custom JWT authentication mechanism.
"""

import logging
from datetime import datetime

from accounts.models.role_model import Role
from accounts.serializers.role_serializer import RoleListSerializer, RoleSerializer
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException

logger = logging.getLogger("django")


class RoleCreateListApiView(BaseAPIView):
    """API endpoint for creating and listing roles."""

    menu_url = "/role/"

    def get(self, request):
        """Retrieve all roles."""
        return self.handle_serializer_data(Role, RoleListSerializer, True)

    def post(self, request):
        """Create a new role."""
        serializer = RoleSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(created_by=request.user, created_at=datetime.now())
            return self.handle_success("Role created successfully.")
        return self.handle_invalid_serializer(serializer)


class RoleDetailsApiView(BaseAPIView):
    """API endpoint for retrieving, updating, and deleting a specific role."""

    menu_url = "/role/"

    def get(self, request, pk):
        """Retrieve a role by reference_id."""
        return self.handle_serializer_data(
            Role, RoleListSerializer, False, reference_id=pk
        )

    def patch(self, request, pk):
        """Update a role."""
        role = Role.objects.get(reference_id=pk)
        role.ensure_not_predefined()

        serializer = RoleSerializer(
            role, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return self.handle_success("Role updated successfully.")
        return self.handle_invalid_serializer(serializer)

    def delete(self, request, pk):
        """Delete a role."""
        try:
            role = Role.objects.get(reference_id=pk)
            role.ensure_not_predefined()
            role.delete()
            return self.handle_success("Role deleted successfully.")
        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)
        except Exception as exe:
            return self.handle_view_exception(exe)      
