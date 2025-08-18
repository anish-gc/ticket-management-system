from accounts.validation.validate_role_menu_permission import (
    EnhancedRoleMenuPermissionService,
)
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException
import logging

logger = logging.getLogger(__name__)


class RoleMenuPermissionCreateListApiView(BaseAPIView):
    menu_url = "/role/menu/permission/mapping/"

    def get(self, request):
        try:
            permissions = EnhancedRoleMenuPermissionService.get_role_permissions()

            return self.handle_success(
                "Role menu permissions retrieved successfully.", permissions
            )
        except Exception as exe:
            logger.error(f"Error retrieving permissions: {str(exe)}", exc_info=True)
            return self.handle_view_exception(exe)

    def post(self, request):
        """Assign menu permissions to a role"""
        try:
            data = request.data

            # Validate required fields
            role_id = data.get("roleId")
            if not role_id:
                raise CustomAPIException("Role cannot be blank.")

            menu_details = data.get("menuDetails", [])
            # Use service to handle the complete workflow
            permissions_count = (
                EnhancedRoleMenuPermissionService.assign_role_permissions(
                    role_id=role_id, menu_details=menu_details, user=request.user
                )
            )

            return self.handle_success(
                "Menu permissions assigned successfully.",
                data={"permissions_created": permissions_count},
            )

        except CustomAPIException as exe:
            logger.warning(f"Validation error in role menu permission: {exe.detail}")
            return self.handle_custom_exception(exe)
        except Exception as exe:
            logger.error(f"Error assigning menu permissions: {str(exe)}", exc_info=True)
            return self.handle_view_exception(exe)


class RoleMenuPermissionDetailsApiView(BaseAPIView):
    menu_url = "/role/menu/permission/mapping/"

    def get(self, request):
        try:
            role_id = request.query_params.get("roleId")  # Optional filtering
            permissions = EnhancedRoleMenuPermissionService.get_role_permissions(
                role_id
            )

            return self.handle_success(
                "Role menu permissions retrieved successfully.", permissions
            )
        except Exception as exe:
            logger.error(f"Error retrieving permissions: {str(exe)}", exc_info=True)
            return self.handle_view_exception(exe)

    def patch(self, request):
        try:
            data = request.data

            # Validate required fields
            role_id = data.get("roleId")
            if not role_id:
                raise CustomAPIException("Role ID cannot be blank.")

            menu_details = data.get("menuDetails", [])

            # Use service to handle the complete workflow
            permissions_count = (
                EnhancedRoleMenuPermissionService.assign_role_permissions(
                    role_id=role_id, menu_details=menu_details, user=request.user
                )
            )

            return self.handle_success(
                f"Menu permissions updated successfully.",
                data={"permissions_created": permissions_count},
            )

        except CustomAPIException as exe:
            logger.warning(f"Validation error in role menu permission: {exe.detail}")
            return self.handle_custom_exception(exe)
        except Exception as exe:
            logger.error(f"Error  menu permissions: {str(exe)}", exc_info=True)
            return self.handle_view_exception(exe)
