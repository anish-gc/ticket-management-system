from accounts.models.role_menu_permission_model import RoleMenuPermission
from accounts.models.role_model import Role
from accounts.validation.validate_role_menu_permission import (
    validate_role_menu_permission,
)
from utilities.api_views import BaseAPIView
from collections import defaultdict
from django.db import transaction
from utilities.exception import CustomAPIException
from utilities.global_functions import model_validation


class RoleMenuPermissionCreateListApiView(BaseAPIView):
    menu_url = "/role/menu/mapping/"

    def get(self, request):
        try:
            permissions = RoleMenuPermission.objects.select_related(
                "role", "menu"
            ).values("role__name", "role__reference_id", "menu__menu_name")

            grouped_permissions = defaultdict(lambda: {"menu": []})

            for perm in permissions:
                role_key = f"{perm['role__role']}"
                if not grouped_permissions[role_key]["menu"]:
                    grouped_permissions[role_key].update(
                        {
                            "role": perm["role__role"],
                            "roleId": perm["role__reference_id"],
                        }
                    )
                grouped_permissions[role_key]["menu"].append(perm["menu__menu_name"])

            json_output = list(grouped_permissions.values())

            return self.handle_success(None, json_output)

        except Exception as exe:
            return self.handle_view_exception(exe)

    def post(self, request):
        try:
            role, role_menu_create = validate_role_menu_permission(request, None)
            with transaction.atomic():
                RoleMenuPermission.objects.filter(role=role).delete()
                RoleMenuPermission.objects.bulk_create(role_menu_create)

            return self.handle_success("Menu permissions assigned successfully.")

        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)

        except Exception as exe:
            return self.handle_view_exception(exe)


class RoleMenuPermissionDetailsApiView(BaseAPIView):
    menu_url = "/role/menu/mapping/"

    def get(self, request):
        try:
            data = request.query_params

            role_id = data["roleId"] if "roleId" in data else ""
            if not role_id:
                raise CustomAPIException("Role can not be blank.")

            role = model_validation(
                Role, "Select a valid Role.", {"reference_id": role_id}
            )

            menus = validate_role_menu_permission.get_menu_structure(role)
            data = {
                "roleId": role.reference_id,
                "role": role.role,
                "menuDetails": menus,
            }

            return self.handle_success(None, data)

        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)

        except Exception as exe:
            return self.handle_view_exception(exe)

    def patch(self, request):
        try:
            branch, role, role_menu_create = validate_role_menu_permission(
                request, None
            )
            with transaction.atomic():
                RoleMenuPermission.objects.filter(role=role).delete()
                RoleMenuPermission.objects.bulk_create(role_menu_create)
            return self.handle_success("Menu permissions update successfully.")

        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)

        except Exception as exe:
            return self.handle_view_exception(exe)
