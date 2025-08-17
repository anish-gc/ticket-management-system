from rest_framework import serializers

from accounts.models.account_model import Account
from utilities import global_parameters
from utilities.exception import CustomAPIException
from utilities.global_functions import validate_password, validate_phone_number


class AccountSerializer(serializers.Serializer):
    username = serializers.CharField(
        error_messages={"required": "Username cannot be blank."}
    )
    address = serializers.CharField(required=False)
    email = serializers.CharField(error_messages={"required": "Email cannot be blank."})
    phoneNumber = serializers.CharField(
        source="phone_number",
        error_messages={"required": "Phone Number cannot be blank."},
    )
    password = serializers.CharField(required=False, write_only=True)

    def create(self, validated_data):
        user = Account.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def validate(self, data):
        try:

            if "phone_number" in data:
                validate_phone_number(data["phone_number"], False)

            if self.instance:
                self._check_unique_fields(data, self.instance.reference_id)
            else:
                self._validate_creation(data)

            return data

        except CustomAPIException as exc:
            raise serializers.ValidationError(
                {global_parameters.ERROR_DETAILS: [exc.detail]}
            )
        except Exception as exc:
            raise Exception(str(exc))

    def _check_unique_fields(self, data, exclude_id):
        if (
            "username" in data
            and Account.objects.filter(username=data["username"])
            .exclude(reference_id=exclude_id)
            .exists()
        ):
            raise CustomAPIException("Username already exists.")

        if (
            "phone_number" in data
            and Account.objects.filter(phone_number=data["phone_number"])
            .exclude(reference_id=exclude_id)
            .exists()
        ):
            raise CustomAPIException("Mobile Number already exists.")

        if (
            "email" in data
            and Account.objects.filter(email=data["email"])
            .exclude(reference_id=exclude_id)
            .exists()
        ):
            raise CustomAPIException("Email already exists.")

    def _validate_creation(self, data):

        if (
            "username" in data
            and Account.objects.filter(username=data["username"]).exists()
        ):
            raise CustomAPIException("Username already exists.")

        if Account.objects.filter(phone_number=data.get("phone_number")).exists():
            raise CustomAPIException("Phone Number already exists.")

        if Account.objects.filter(email=data.get("email")).exists():
            raise CustomAPIException("Email already exists.")
        if not data.get("password"):
            raise CustomAPIException("Password cannot be blank.")
        if not validate_password(data["password"]):
            raise CustomAPIException(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit, and be at least 8 characters long."
            )


class AccountListSerializer(serializers.Serializer):
    referenceId = serializers.CharField(read_only=True, source="reference_id")
    username = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    phoneNumber = serializers.CharField(source="phone_number", read_only=True)
    role = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        """Customize representation for consistent API response."""
        data = super().to_representation(instance)
        data["email"] = data["email"] or ""  # Ensure email is never None
        data["role"] = data["role"] or ""
        return data
