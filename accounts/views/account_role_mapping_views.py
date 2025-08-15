"""This module used fot login and register login will be done through custom authetication."""

import logging

from django.db.models import F, Value as V
from django.db.models.functions import Concat

from accounts.models.account_model import Account
from accounts.models.role_model import Role
from accounts.validation.validate_user_role_mapping import validate_user_role_mapping
from utilities.api_views import BaseAPIView
from utilities.exception import CustomAPIException
from utilities.global_functions import model_validation


logger = logging.getLogger("django")


class AccountRoleMappingCreateListApiView(BaseAPIView):
    menu_url = "/role/mapping/"

    def get(self, request):
        try:
            user_role_data = []

            user_role_data = Account.objects.filter(
                role__isnull=False, is_active=True
            ).values(
                referenceId=F("reference_id"),
                roleId=F("role__reference_id"),
                mobileNumber=F("phone_number"),
                roleType=F("role__name"),
                username=F("username"),
            )
            return self.handle_success(None, user_role_data)

        except Exception as exe:
            return self.handle_view_exception(exe)

    def post(self, request):
        try:
            users_to_update = validate_user_role_mapping(request)
            Account.objects.bulk_update(users_to_update, ["role"])
            return self.handle_success("User Role created successfully.")

        except CustomAPIException as exe:
            return self.handle_custom_exception(exe)

        except Exception as exe:
            return self.handle_view_exception(exe)


class AccountRoleMappingDetailsApiView(BaseAPIView):
    menu_url = "/role/mapping/"

    def get(self, request, pk):
        try:
            user = Account.objects.get(reference_id=pk)
            user_role_data = {
                "userId": user.reference_id,
                "roleId": user.role.reference_id,
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
            user = Account.objects.filter(reference_id=pk)
            user.role = None
            user.save()
            return self.handle_success("User Role deleted successfully.")

        except Exception as exe:
            return self.handle_view_exception(exe)
