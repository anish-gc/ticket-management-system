from accounts.models.menu_model import Menu
from utilities.exception import CustomAPIException

import logging

logger = logging.getLogger(__name__)

from django.db.models import Prefetch
from django.core.cache import cache


from django.db.models import Prefetch, Q
from django.core.cache import cache


def get_menu_structure(role_id=None, is_superuser=False):
    """
    Get menu structure with permissions for a role or superuser
    Args:
        role_id: ID of the role to check permissions
        is_superuser: Whether the user has superuser privileges
    Returns:
        List of menu items with permissions
    Raises:
        CustomAPIException: If access is denied
    """
    # Validate non-superuser access
    if not is_superuser:
        if not role_id:
            raise CustomAPIException("Access restricted. Role ID required")

        # Check cache first
        cache_key = f"menu_structure_{role_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # Single query to get all permitted menus with permissions
        permitted_menus = (
            Menu.objects.filter(role_permissions__role_id=role_id, visibility=True)
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=Menu.objects.filter(visibility=True).order_by(
                        "display_order"
                    ),
                )
            )
            .order_by("display_order")
        )

        if not permitted_menus.exists():
            raise CustomAPIException("Access denied. No menu permissions for this role")

        # Build menu structure
        menu_data = []
        for menu in permitted_menus.filter(parent__isnull=True):
            menu_data.append(build_menu_item(menu, is_superuser=False))

        # Cache for 1 hour
        cache.set(cache_key, menu_data, 3600)
        return menu_data

    # Superuser case - simplified with all permissions
    top_level_menus = (
        Menu.objects.filter(parent__isnull=True, visibility=True)
        .prefetch_related(
            Prefetch(
                "children",
                queryset=Menu.objects.filter(visibility=True).order_by("display_order"),
            )
        )
        .order_by("display_order")
    )

    return [build_menu_item(menu, is_superuser=True) for menu in top_level_menus]


def build_menu_item(menu, is_superuser=None):
    """
    Build a single menu item with permissions
    Args:
        menu: Menu instance
        is_superuser: Whether to apply all permissions
    Returns:
        Dict containing menu data and permissions
    """
    data = {
        "id": menu.reference_id,
        "name": menu.menu_name,
        "url": menu.menu_url,
        "icon": menu.icon,
        "createUrl": menu.create_url,
        "listUrl": menu.list_url,
    }

    # Handle permissions
    if is_superuser:
        data.update(
            {"isView": True, "isCreate": True, "isUpdate": True, "isDelete": True}
        )
    else:
        # Permissions are already filtered in the main query
        permission = menu.role_permissions.first()
        data.update(
            {
                "isView": permission.can_view if permission else False,
                "isCreate": permission.can_create if permission else False,
                "isUpdate": (
                    permission.can_update if permission else False
                ),  # Consistent naming
                "isDelete": permission.can_delete if permission else False,
            }
        )

    # Build submenus if they exist
    if hasattr(menu, "children") and menu.children.exists():
        data["subMenus"] = [
            build_menu_item(child, is_superuser) for child in menu.children.all()
        ]
    else:
        data["subMenus"] = None

    return data
