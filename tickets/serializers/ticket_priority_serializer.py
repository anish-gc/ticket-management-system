import datetime
from rest_framework import serializers
from tickets.models.ticket_priority_model import TicketPriority
from utilities import global_parameters


class TicketPrioritySerializer(serializers.Serializer):
    referenceId = serializers.CharField(source="reference_id", read_only=True)
    name = serializers.CharField(
        error_messages={"required": "Priority name can not be blank."}
    )
    code = serializers.CharField(
        error_messages={"required": "Priority code can not be blank."}
    )
    description = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.IntegerField(default=0)
    color = serializers.CharField(default="#28a745")
    slaHours = serializers.IntegerField(
        source="sla_hours",
        required=False,
        allow_null=True,
        help_text="SLA response time in hours",
    )
    isDefault = serializers.BooleanField(default=False, source="is_default")


    def create(self, validated_data):
        if validated_data.get("is_default", False):
            TicketPriority.objects.update(is_default=False)
        return TicketPriority.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.code = validated_data.get("code", instance.code)
        instance.description = validated_data.get("description", instance.description)
        instance.weight = validated_data.get("weight", instance.weight)
        instance.color = validated_data.get("color", instance.color)
        instance.sla_hours = validated_data.get("sla_hours", instance.sla_hours)

        if validated_data.get("is_default", instance.is_default):
            TicketPriority.objects.update(is_default=False)
            instance.is_default = True
        else:
            instance.is_default = validated_data.get("is_default", instance.is_default)

        instance.save()
        return instance

    def validate(self, data):
        name = str(data.get("name", "")).strip()
        code = str(data.get("code", "")).strip()

        # Name uniqueness check

        qs_name = TicketPriority.objects.filter(name__iexact=name)
        if self.instance:
            qs_name = qs_name.exclude(reference_id=self.instance.reference_id)
        if qs_name.exists():
            raise serializers.ValidationError(
                {
                    global_parameters.ERROR_DETAILS: [
                        f"Ticket priority with name '{name}' already exists."
                    ]
                }
            )

        # Code uniqueness check
        qs_code = TicketPriority.objects.filter(code__iexact=code)
        if self.instance:
            qs_code = qs_code.exclude(reference_id=self.instance.reference_id)
        if qs_code.exists():
            raise serializers.ValidationError(
                {
                    global_parameters.ERROR_DETAILS: [
                        f"Ticket priority with code '{code}' already exists."
                    ]
                }
            )

        # Normalize values before saving
        data["name"] = name
        data["code"] = code.upper()
        return data


class TicketPriorityListSerializer(serializers.Serializer):
    referenceId = serializers.CharField(source="reference_id", read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    weight = serializers.IntegerField(read_only=True)
    slaHours = serializers.IntegerField(read_only=True, source='sla_hours')
