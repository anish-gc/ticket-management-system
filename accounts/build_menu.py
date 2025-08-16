from accounts.models.menu_model import Menu
from accounts.models.role_menu_permission_model import RoleMenuPermission
from utilities.exception import CustomAPIException

import logging

logger = logging.getLogger(__name__)


def get_menu_structure(role_id):
    if not role_id:
        raise CustomAPIException(
            "Access restricted. You must have the specified role to continue"
        )
    if not RoleMenuPermission.objects.filter(role_id=role_id).exists():
        raise CustomAPIException(
            "Access denied. Your current role does not have the permissions to access this menu."
        )

    role_menus = RoleMenuPermission.objects.filter(role_id=role_id)
    menu_ids = role_menus.filter(menu_id__parent__isnull=True).values_list(
        "menu_id", flat=True
    )

    # Fetch parent menus that match the role_id and are not deleted
    parent_menus = Menu.objects.filter(id__in=menu_ids, visibility=True).order_by(
        "display_number"
    )

    menu_data = []
    for menu in parent_menus:
        menu_data.append(build_menu_item(menu, role_menus))

    return menu_data


def build_menu_item(menu, role_menus):
    # Fetch permissions for the given menu from the pre-fetched role_menus
    role_permission = role_menus.filter(menu=menu).first()

    is_view = role_permission.can_view if role_permission else False
    is_create = role_permission.can_create if role_permission else False
    is_update = role_permission.can_update if role_permission else False
    is_delete = role_permission.can_delete if role_permission else False

    # Fetch submenus that match the role_id and are not deleted
    submenu_ids = role_menus.values_list("menu_id", flat=True)
    submenus = Menu.objects.filter(
        id__in=submenu_ids, parent=menu, visibility=True
    ).order_by("display_number")

    submenu_data = [build_menu_item(submenu, role_menus) for submenu in submenus]

    data = {
        "id": menu.reference_id,
        "name": menu.menu_name,
        "url": menu.menu_url,
        "icon": menu.icon,
        "createUrl": menu.create_url,
        "listUrl": menu.list_url,
        "subMenus": submenu_data if submenu_data else None,
    }
    if not submenu_data:
        data["isView"] = is_view
        data["isCreate"] = is_create
        data["isUpdate"] = is_update
        data["isDelete"] = is_delete

    return data
