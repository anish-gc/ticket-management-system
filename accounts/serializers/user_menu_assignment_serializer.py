from rest_framework import serializers

from accounts.models.account_model import Account
from accounts.models.menu_model import Menu
from accounts.models.user_menu_assignment_model import UserMenuAssignment
from utilities.global_functions import model_validation


class UserMenuAssignmentSerializer(serializers.Serializer):
    accountId = serializers.CharField(
        source="account", error_messages={"required": "Account cannot be blank"}
    )
    menuId = serializers.CharField(
        source="menu", error_messages={"required": "Menu can not be blank."}
    )

    def create(self, validated_data):
        return UserMenuAssignment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance
    def validate(self, data):
        account_reference_id = data.get("account")
        account = model_validation(
            Account,
            "Select a valid account to assign menu",
            {"reference_id": account_reference_id},
        )

        menu_reference_id = data.get("menu")
        menu = model_validation(
            Menu,
            "Select a valid menu for account",
            {"reference_id": menu_reference_id},
        )

        data["account"] = account
        data["menu"] = menu

        return data


class UserMenuAssignmentListSerializer(serializers.Serializer):
    """Read-only serializer for UserMenuAssignment"""

    referenceId = serializers.CharField(read_only=True, source="reference_id")
    accountReferenceId = serializers.CharField(
        source="account.reference_id", read_only=True
    )
    accountUsername = serializers.CharField(source="account.username", read_only=True)

    menuReferenceId = serializers.CharField(source="menu.reference_id", read_only=True)
    menuName = serializers.CharField(source="menu.menu_name", read_only=True)

    assignedBy = serializers.CharField(source="assigned_by.username", read_only=True)
