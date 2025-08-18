import logging

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from accounts.models.account_model import Account
from accounts.models.menu_model import Menu
from accounts.models.role_menu_permission_model import RoleMenuPermission
from accounts.models.user_menu_assignment_model import UserMenuAssignment


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

            # First check user-specific menu assignments
            user_assignment_query = {
                "account_id": request.user.id,
                "menu_id": menu.id,
                permission_field: True,
            }

            # Check if user has specific menu assignment with required permission
            user_has_assignment = UserMenuAssignment.objects.filter(
                **user_assignment_query
            ).exists()

            if user_has_assignment:
                return True

            # If no user-specific assignment, fall back to role-based permissions
            role_query = {
                "menu_id": menu.id,
                "role_id": user_details.role_id,
                permission_field: True,
            }

            return permission_check_func(role_query)

        except (Account.DoesNotExist, Menu.DoesNotExist) as e:
            logger.error(str(e), exc_info=True)
            return False
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return False

    @classmethod
    def check_user_has_menu_access(cls, user_id, menu_url):
        """Check if user has any access to a menu (either through role or direct assignment)"""
        try:
            menu = Menu.objects.get(menu_url=menu_url)

            # Check user-specific assignments first
            user_assignment = UserMenuAssignment.objects.filter(
                account_id=user_id, menu_id=menu.id
            ).exists()

            if user_assignment:
                return True

            # Check role-based permissions
            user_details = Account.objects.select_related("role").get(id=user_id)
            role_permission = RoleMenuPermission.objects.filter(
                menu_id=menu.id, role_id=user_details.role_id
            ).exists()

            return role_permission

        except (Account.DoesNotExist, Menu.DoesNotExist):
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


# Alternative implementation with more explicit logic
class EnhancedCustomPermission(permissions.BasePermission):
    """
    Enhanced permission class that checks both user-specific menu assignments
    and role-based permissions with priority given to user assignments.
    """

    ACTION_MAPPING = {
        "C": "can_create",
        "L": "can_view",
        "U": "can_update",
        "D": "can_delete",
    }

    def has_permission(self, request, view):
        try:
            if request.user.is_superuser:
                return True

            action = getattr(view, "action", None)
            menu_url = getattr(view, "menu_url", None)

            if not action or not menu_url:
                return False

            if action not in self.ACTION_MAPPING:
                return False

            permission_field = self.ACTION_MAPPING[action]

            # Get menu object
            try:
                menu = Menu.objects.get(menu_url=menu_url)
            except Menu.DoesNotExist:
                logger.error(f"Menu with URL {menu_url} not found")
                return False
            print('iamhere')

            # Priority 1: Check user-specific menu assignments
            user_assignment = UserMenuAssignment.objects.filter(
                account_id=request.user.id, menu_id=menu.id
            ).first()

            if user_assignment:
                # If user has specific assignment, use that permission
                has_permission = getattr(user_assignment, permission_field, False)
                if not has_permission:
                    raise PermissionDenied(
                        f"You do not have {permission_field.replace('can_', '')} permission for this menu."
                    )
                return True

            # Priority 2: Fall back to role-based permissions
            try:
                user_details = Account.objects.select_related("role").get(
                    id=request.user.id
                )
                role_permission = RoleMenuPermission.objects.filter(
                    menu_id=menu.id,
                    role_id=user_details.role_id,
                    **{permission_field: True},
                ).exists()

                if not role_permission:
                    raise PermissionDenied(
                        "You do not have permission to perform this action."
                    )

                return True

            except Account.DoesNotExist:
                logger.error(f"Account with ID {request.user.id} not found")
                return False

        except PermissionDenied:
            raise
        except Exception as e:
            logger.error(f"Permission check failed: {str(e)}", exc_info=True)
            raise PermissionDenied("You do not have permission to perform this action.")


# Utility function to get user's effective menus (combines role and user assignments)
def get_user_effective_menus(user_id):
    """
    Get all menus a user has access to, combining role-based and user-specific assignments.
    User-specific assignments take priority over role-based permissions.
    """
    try:
        user = Account.objects.select_related("role").get(id=user_id)

        # Get user-specific menu assignments
        user_menus = {}
        user_assignments = UserMenuAssignment.objects.filter(
            account_id=user_id
        ).select_related("menu")

        for assignment in user_assignments:
            user_menus[assignment.menu.id] = {
                "menu": assignment.menu,
                "can_view": assignment.can_view,
                "can_create": assignment.can_create,
                "can_update": assignment.can_update,
                "can_delete": assignment.can_delete,
                "source": "user_assignment",
            }

        # Get role-based permissions for menus not in user assignments
        role_permissions = RoleMenuPermission.objects.filter(
            role_id=user.role_id
        ).select_related("menu")

        for permission in role_permissions:
            if permission.menu.id not in user_menus:
                user_menus[permission.menu.id] = {
                    "menu": permission.menu,
                    "can_view": permission.can_view,
                    "can_create": permission.can_create,
                    "can_update": permission.can_update,
                    "can_delete": permission.can_delete,
                    "source": "role_permission",
                }

        return list(user_menus.values())

    except Account.DoesNotExist:
        logger.error(f"Account with ID {user_id} not found")
        return []
    except Exception as e:
        logger.error(f"Error getting user menus: {str(e)}", exc_info=True)
        return []
