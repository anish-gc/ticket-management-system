from accounts.models.menu_model import Menu
from accounts.models.role_menu_permission_model import RoleMenuPermission
from accounts.models.role_model import Role
from utilities.exception import CustomAPIException
from utilities.global_functions import generate_uuid, model_validation, validate_boolean
from typing import List, Dict, Any
from collections import defaultdict
from django.db import transaction
from django.utils import timezone
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RoleMenuPermissionConfig:
    """Configuration constants for role menu permissions"""

    PERMISSION_FIELDS = ["isCreate", "isView", "isEdit", "isDelete"]
    DEFAULT_PERMISSIONS = {
        "isCreate": False,
        "isView": True,  # Usually view should be default True
        "isEdit": False,
        "isDelete": False,
    }
    BATCH_SIZE = 100

    @classmethod
    def get_permission_value(cls, data: dict, field: str) -> bool:
        """Get permission value with default fallback"""
        return data.get(field, cls.DEFAULT_PERMISSIONS[field])


class EnhancedRoleMenuPermissionService:
    PERMISSION_FIELDS = ["isCreate", "isView", "isEdit", "isDelete"]

    @classmethod
    def get_role_permissions(cls, role_id: str = None) -> List[Dict[str, Any]]:
        """
        Get role menu permissions with optional role filtering

        Args:
            role_id: Optional role ID to filter by

        Returns:
            List of role permission dictionaries
        """
        # Build queryset
        queryset = RoleMenuPermission.objects.select_related("role", "menu")

        if role_id:
            queryset = queryset.filter(role__reference_id=role_id)

        permissions = queryset.values(
            "role__name",
            "role__reference_id",
            "menu__menu_name",
            "menu__reference_id",
            "can_create",
            "can_view",
            "can_update",
            "can_delete",
        ).order_by("role__name", "menu__menu_name")

        # Group by role
        grouped_permissions = defaultdict(lambda: {"menuDetails": []})

        for perm in permissions:
            role_key = perm["role__reference_id"]

            # Add role info if first menu for this role
            if not grouped_permissions[role_key]["menuDetails"]:
                grouped_permissions[role_key].update(
                    {
                        "role": perm["role__name"],
                        "roleId": perm["role__reference_id"],
                    }
                )

            # Add menu details
            grouped_permissions[role_key]["menuDetails"].append(
                {
                    "menuName": perm["menu__menu_name"],
                    "menuId": perm["menu__reference_id"],
                    "isCreate": perm["can_create"],
                    "isView": perm["can_view"],
                    "isEdit": perm["can_update"],
                    "isDelete": perm["can_delete"],
                }
            )

        return list(grouped_permissions.values())

    @classmethod
    def validate_permission_data(
        cls, permission_data: Dict[str, Any], index: int = None
    ) -> None:
        """Validate individual permission data"""
        item_ref = f" for item {index + 1}" if index is not None else ""
        if not permission_data.get("menuId"):
            raise CustomAPIException(f"Menu ID cannot be blank{item_ref}.")
        # Validate permission field types
        for field in cls.PERMISSION_FIELDS:
            value = permission_data.get(field)
            if value is not None and not isinstance(value, bool):
                raise CustomAPIException(
                    f"Field '{field}' must be a boolean value{item_ref}."
                )

        # Ensure at least one permission is True
        if not any(
            permission_data.get(field, False) for field in cls.PERMISSION_FIELDS
        ):
            raise CustomAPIException(
                f"At least one permission must be enabled{item_ref}."
            )

    @classmethod
    def validate_menu_details(cls, menu_details: List[Dict[str, Any]]) -> None:
        """Validate the entire menu details list"""
        if not menu_details:
            raise CustomAPIException("Menu Details cannot be blank.")

        if not isinstance(menu_details, list):
            raise CustomAPIException("Menu Details must be a list.")

     
        # Check for duplicate menu IDs
        menu_ids = [
            detail.get("menuId") for detail in menu_details if detail.get("menuId")
        ]
        if len(menu_ids) != len(set(menu_ids)):
            raise CustomAPIException("Duplicate menu entries are not allowed.")

        # Validate each permission data with index for better error messages
        for index, menu_detail in enumerate(menu_details):
            cls.validate_permission_data(menu_detail, index)

    @classmethod
    def bulk_validate_menus(cls, menu_ids: List[str]) -> Dict[str, Any]:
        """Validate all menus exist and return them as a dictionary"""
        existing_menus = Menu.objects.filter(reference_id__in=menu_ids)
        existing_menu_dict = {menu.reference_id: menu for menu in existing_menus}

        if len(existing_menu_dict) != len(set(menu_ids)):
            missing_ids = set(menu_ids) - set(existing_menu_dict.keys())
            raise CustomAPIException(f"Invalid menu IDs: {', '.join(missing_ids)}")

        return existing_menu_dict

    @classmethod
    def create_role_menu_permissions(
        cls, role, menu_details: List[Dict[str, Any]], user
    ) -> List[RoleMenuPermission]:
        """Create permissions with configuration-based defaults"""
        menu_ids = [details["menuId"] for details in menu_details]
        menu_dict = cls.bulk_validate_menus(menu_ids)

        role_menu_permissions = []
        current_time = timezone.now()

        for details in menu_details:
            menu = menu_dict[details["menuId"]]

            role_menu_permissions.append(
                RoleMenuPermission(
                    reference_id=generate_uuid(),
                    menu=menu,
                    role=role,
                    can_create=RoleMenuPermissionConfig.get_permission_value(
                        details, "isCreate"
                    ),
                    can_view=RoleMenuPermissionConfig.get_permission_value(
                        details, "isView"
                    ),
                    can_update=RoleMenuPermissionConfig.get_permission_value(
                        details, "isEdit"
                    ),
                    can_delete=RoleMenuPermissionConfig.get_permission_value(
                        details, "isDelete"
                    ),
                    created_by=user,
                    created_at=current_time,
                )
            )
        return role_menu_permissions

    @classmethod
    def assign_role_permissions(
        cls, role_id: str, menu_details: List[Dict[str, Any]], user
    ) -> int:
        """Complete workflow for assigning permissions to a role"""
        # Validate role
        role = model_validation(Role, "Select a valid role.", {"reference_id": role_id})
        # Validate menu details
        cls.validate_menu_details(menu_details)

        # Create and assign permissions
        with transaction.atomic():
            # Delete existing permissions
            deleted_count = RoleMenuPermission.objects.filter(role=role).delete()[0]

            # Create new permissions
            permissions = cls.create_role_menu_permissions(role, menu_details, user)
            created_permissions = RoleMenuPermission.objects.bulk_create(
                permissions, batch_size=100
            )

            logger.info(
                f"Updated permissions for role {role.reference_id}: "
                f"deleted {deleted_count}, created {len(created_permissions)}"
            )

        return len(created_permissions)

