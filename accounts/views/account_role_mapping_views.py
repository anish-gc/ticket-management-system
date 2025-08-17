"""This module used fot login and register login will be done through custom authetication."""

import logging

from django.db.models import F, Value as V
from django.db import transaction
from accounts.models.account_model import Account
from accounts.models.role_model import Role
from accounts.validation.validate_user_role_mapping import prepare_user_role_updates
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException
from utilities.global_functions import model_validation


logger = logging.getLogger("django")


class AccountRoleMappingCreateListApiView(BaseAPIView):
    menu_url = "/account/roles/mapping/"

    def get(self, request):
        try:
            user_role_data = (
                Account.objects.filter(role__isnull=False, is_active=True)
                .annotate(
                    accountId=F("reference_id"),
                    roleId=F("role__reference_id"),
                    roleName=F("role__name"),
                )
                .values("accountId", "username", "roleId", "roleName")
            )

            return self.handle_success(None, list(user_role_data))
        except Exception as exc:
            return self.handle_exception(exc)

    def post(self, request):
        try:
            users_to_update = prepare_user_role_updates(request)
            with transaction.atomic():  # Add transaction for safety
                updated_count = Account.objects.bulk_update(
                    users_to_update,
                    ["role"],
                    batch_size=1000,  # Optional: optimize for large updates
                )

            return self.handle_success(
                f"Successfully updated roles for {updated_count} users.",
                data={"updated_count": updated_count},
            )

        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)

        except Exception as exe:
            return self.handle_view_exception(exe)


class AccountRoleMappingDetailsApiView(BaseAPIView):
    menu_url = "/account/roles/mapping/"

    def get(self, request, pk):
        try:
            user = Account.objects.get(reference_id=pk)
            user_role_data = {
                "userId": user.reference_id,
                "userName": user.username,
                "roleId": user.role.reference_id,
                "role": user.role.name,
            }
            return self.handle_success(None, user_role_data)

        except Exception as exe:
            return self.handle_view_exception(exe)

    def patch(self, request, pk):
        try:
            user = Account.objects.get(reference_id=pk)
            data = request.data
            role_id = data["roleId"] if "roleId" in data else ""
            if not role_id:
                raise CustomAPIException("Role can not blank.")
            role = model_validation(
                Role,
                "Select a valid role.",
                {
                    "reference_id": role_id,
                },
            )

            user.role = role
            user.updated_by = request.user
            user.save()
            return self.handle_success("User Role updated successfully.")

        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)

        except Exception as exe:
            return self.handle_view_exception(exe)

    def delete(self, request, pk):
        try:
            user = Account.objects.get(reference_id=pk)
            
            user.role = None
            user.save()
            return self.handle_success("User Role deleted successfully.")

        except Exception as exe:
            return self.handle_view_exception(exe)
