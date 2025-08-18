from accounts.models.menu_model import Menu
from utilities.exception import CustomAPIException

import logging

logger = logging.getLogger(__name__)

from django.core.cache import cache


from django.db.models import Prefetch, Q
from accounts.models import UserMenuAssignment


def get_menu_structure(role_id=None, is_superuser=False, user_id=None):
    """
    Get menu structure with role-based or user-specific assignments
    Args:
        role_id: Role ID of the logged-in user
        is_superuser: Whether the user has superuser privileges
        user_id: The logged-in user's ID (for UserMenuAssignment)
    """

    # Superuser -> return all menus
    if is_superuser:
        top_level_menus = (
            Menu.objects.filter(parent__isnull=True, visibility=True)
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
        return [build_menu_item(menu, is_superuser=True) for menu in top_level_menus]

    if not role_id:
        raise CustomAPIException("Access restricted. Role ID required")

    # ✅ Step 1: Check if user has explicit menu assignments
    user_assigned_menus = Menu.objects.filter(
        id__in=UserMenuAssignment.objects.filter(account_id=user_id).values_list(
            "menu_id", flat=True
        ),
        visibility=True,
    )
    if user_assigned_menus.exists():
        top_level_menus = user_assigned_menus.filter(parent__isnull=True).order_by(
            "display_order"
        )
        return [build_user_assigned_menu_item(menu, user_id) for menu in top_level_menus]

    # ✅ Step 2: If no user-specific assignment, fallback to role-based
    cache_key = f"menu_structure_{role_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    permitted_menus = (
        Menu.objects.filter(role_permissions__role_id=role_id, visibility=True)
        .prefetch_related(
            Prefetch(
                "children",
                queryset=Menu.objects.filter(visibility=True).order_by("display_order"),
            )
        )
        .order_by("display_order")
    )

    if not permitted_menus.exists():
        raise CustomAPIException("Access denied. Please ask admin to set menu for you")

    menu_data = [
        build_menu_item(menu, is_superuser=False)
        for menu in permitted_menus.filter(parent__isnull=True)
    ]

    cache.set(cache_key, menu_data, 3600)
    return menu_data



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


def build_user_assigned_menu_item(menu, user_id):
    """
    Build a single menu item for user-assigned menus
    Args:
        menu: Menu instance
        user_id: User ID to check for assignments
    Returns:
        Dict containing menu data with basic permissions
    """
    data = {
        "id": menu.reference_id,
        "name": menu.menu_name,
        "url": menu.menu_url,
        "icon": menu.icon,
        "createUrl": menu.create_url,
        "listUrl": menu.list_url,
    }

    # For user-assigned menus, you have a few options:
    # Option 1: Give basic view-only permissions by default
    data.update(
        {
            "isView": True,
            "isCreate": False,
            "isUpdate": False,
            "isDelete": False,
        }
    )
    
    user_assignment = UserMenuAssignment.objects.filter(
        account_id=user_id, menu=menu
    ).first()
    
    if user_assignment:
        # Use permissions from UserMenuAssignment
        data.update(
            {
                "isView": user_assignment.can_view,
                "isCreate": user_assignment.can_create,
                "isUpdate": user_assignment.can_update,
                "isDelete": user_assignment.can_delete,
            }
        )
    else:
        # Fallback to default permissions if assignment not found
        data.update(
            {
                "isView": True,
                "isCreate": False,
                "isUpdate": False,
                "isDelete": False,
            }
        )

    # Option 2: If you want to extend UserMenuAssignment model to include permissions
    # you could add permission fields to UserMenuAssignment and use them here
    
    # Option 3: If you want to inherit role permissions when available
    # Uncomment the code below:
    """
    # Try to get role permissions for this menu if available
    user_assignment = UserMenuAssignment.objects.filter(
        account_id=user_id, menu=menu
    ).first()
    
    if user_assignment and hasattr(user_assignment.account, 'role'):
        role_id = user_assignment.account.role.id
        permission = menu.role_permissions.filter(role_id=role_id).first()
        if permission:
            data.update(
                {
                    "isView": permission.can_view,
                    "isCreate": permission.can_create,
                    "isUpdate": permission.can_update,
                    "isDelete": permission.can_delete,
                }
            )
        else:
            # Default permissions if no role permission found
            data.update(
                {
                    "isView": True,
                    "isCreate": False,
                    "isUpdate": False,
                    "isDelete": False,
                }
            )
    """

    # Build submenus if they exist
    if hasattr(menu, "children") and menu.children.exists():
        # Filter children that are also assigned to the user
        assigned_child_ids = UserMenuAssignment.objects.filter(
            account_id=user_id
        ).values_list("menu_id", flat=True)
        
        assigned_children = menu.children.filter(
            id__in=assigned_child_ids, visibility=True
        ).order_by("display_order")
        
        if assigned_children.exists():
            data["subMenus"] = [
                build_user_assigned_menu_item(child, user_id) 
                for child in assigned_children
            ]
        else:
            data["subMenus"] = None
    else:
        data["subMenus"] = None

    return data

