import datetime
from rest_framework import serializers
from accounts.models.role_model import Role
from utilities import global_parameters


class RoleSerializer(serializers.Serializer):
    referenceId = serializers.CharField(source="reference_id", read_only=True)
    name = serializers.CharField(
        error_messages={"required": "Role name can not be blank."}
    )

    def create(self, validated_data):
        return Role.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.is_predefined = validated_data.get(
            "is_predefined", instance.is_predefined
        )
        instance.updated_by = self.context.get("user")
        instance.updated_at = datetime.datetime.now()
        instance.save()
        return instance

    def validate(self, data):
        role_name = str(data["name"]).strip().lower()

        qs = Role.objects.filter(name__iexact=role_name)
        if self.instance:
            qs = qs.exclude(reference_id=self.instance.reference_id)

        if qs.exists():
            raise serializers.ValidationError(
                {
                    global_parameters.ERROR_DETAILS: [
                        f"Role with name '{role_name}' already exists."
                    ]
                }
            )

        # Store normalized value
        data["name"] = role_name
        return data


class RoleListSerializer(serializers.Serializer):
    referenceId = serializers.CharField(source="reference_id", read_only=True)
    name = serializers.CharField( read_only=True)

