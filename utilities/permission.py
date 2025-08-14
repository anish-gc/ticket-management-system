import logging

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from accounts.models.account_model import Account
from accounts.models.menu_model import Menu
from accounts.models.role_menu_permission_model import RoleMenuPermission


logger = logging.getLogger("django")


class BasePermissionChecker:
    ACTION_MAPPING = {
        "C": "can_create",
        "L": "can_view",
        "U": "can_update",
        "D": "can_delete",
    }

    @classmethod
    def check_permission(cls, request, action, menu_url, permission_check_func):
        try:
            if action not in cls.ACTION_MAPPING:
                return False

            permission_field = cls.ACTION_MAPPING[action]
            user_details = Account.objects.select_related("role").get(
                id=request.user.id
            )
            menu = Menu.objects.get(menu_url=menu_url)
            query = {
                "menu_id": menu.id,
                "role_id": user_details.role_id,
                permission_field: True,
            }

            return permission_check_func(query)

        except (Account.DoesNotExist, Menu.DoesNotExist) as e:
            logger.error(str(e), exc_info=True)
            return False
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return False


class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.is_superuser:
                return True

            action = getattr(view, "action", None)
            menu_url = getattr(view, "menu_url", None)

            if not action or not menu_url:
                return False

            has_perm = BasePermissionChecker.check_permission(
                request,
                action,
                menu_url,
                lambda query: RoleMenuPermission.objects.filter(**query).exists(),
            )

            if not has_perm:
                raise PermissionDenied(
                    "You do not have permission to perform this action."
                )
            return True

        except Exception:
            raise PermissionDenied("You do not have permission to perform this action.")