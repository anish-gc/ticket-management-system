import logging

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from accounts.models.account_model import Account
from accounts.models.menu_model import Menu
from accounts.models.role_menu_permission_model import RoleMenuPermission


logger = logging.getLogger("django")

class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            action = getattr(view, 'action', None)
            menu_url = getattr(view, 'menu_url', None)
            if not action or not menu_url:
                return False

            if not check_user_permission(request, action, menu_url):
                raise PermissionDenied("You do not have permission to perform this action.")
            return True

        except Exception:
            raise PermissionDenied("You do not have permission to perform this action.")

def check_user_permission(request, action, menu_url):
    try:
        
       

        user_details = Account.objects.select_related('role').get(user_id=request.user.id)
        menu = Menu.objects.get(menu_url=menu_url)

        action_mapping = {
            'C': 'can_create',
            'L': 'can_view',
            'U': 'can_update',
            'D': 'can_delete'
        }

        permission_field = action_mapping.get(action)
        if not permission_field:
            return False

        query = {
            "menu_id": menu.id,
            "role_id": user_details.role_id,
            permission_field: True
        }

        return RoleMenuPermission.objects.filter(**query).exists()

    except (Account.DoesNotExist, Menu.DoesNotExist) as e:
        logger.error(str(e), exc_info=True)
        return False

    except Exception as e:
        logger.error(str(e), exc_info=True)
        return False



class BasePermissionCheck(permissions.BasePermission):
    def has_permission(self, request, view, menu_check_func):
        try:
            action = getattr(view, 'action', None)
            menu_url = getattr(view, 'menu_url', None)

            if not action or not menu_url:
                return False

            has_perm = self.check_permission(request, action, menu_url, menu_check_func)
            
            if not has_perm:
                raise PermissionDenied("You do not have permission to perform this action.")
            return has_perm

        except Exception:
            raise PermissionDenied("You do not have permission to perform this action.")

    def check_permission(self, request, action, menu_url, menu_check_func):
        try:
            action_mapping = {
                'C': 'can_create',
                'L': 'can_view',
                'U': 'can_update',
                'D': 'can_delete'
            }

            query = {"menu_url": menu_url}

            if action in action_mapping:
                query[action_mapping[action]] = True
            else:
                return False

            menu = Menu.objects.filter(**query).first()
            if not menu:
                return False

            return menu_check_func(menu)

        except Exception as exe:
            logger.error(str(exe), exc_info=True)
            return False


