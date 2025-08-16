import datetime
from rest_framework import serializers
from tickets.models.ticket_status_model import TicketStatus
from utilities import global_parameters


class TicketStatusSerializer(serializers.Serializer):
    STATUS_WEIGHTS = {
        "open": 1,
        "in_progress": 2,
        "pending": 3,
        "resolved": 4,
        "closed": 5,
        "cancelled": 6,
    }
    referenceId = serializers.CharField(source="reference_id", read_only=True)
    name = serializers.CharField(
        error_messages={"required": "Status name can not be blank."}
    )
    code = serializers.CharField(
        error_messages={"required": "Status code can not be blank."}
    )
    description = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.IntegerField(required=False)
    statusType = serializers.ChoiceField(
        choices=TicketStatus.STATUS_TYPE_CHOICES,
        source="status_type",
        error_messages={
            "invalid_choice": "Invalid status type. Please choose one of: open, in_progress, pending, resolved, closed, cancelled."
        },
    )
    isDefault = serializers.BooleanField(default=False, source="is_default")

    def create(self, validated_data):
        print(validated_data)
        if validated_data.get("is_default", False):
            TicketStatus.objects.update(is_default=False)
        return TicketStatus.objects.create(**validated_data)

    def update(self, instance, validated_data):
        print(validated_data)
        instance.name = validated_data.get("name", instance.name)
        instance.code = validated_data.get("code", instance.code)
        instance.description = validated_data.get("description", instance.description)
        instance.weight = validated_data.get("weight", instance.weight)
        instance.status_type = validated_data.get("statusType", instance.status_type)
        if validated_data.get("is_default", instance.is_default):
            TicketStatus.objects.update(is_default=False)
            instance.is_default = True
        else:
            instance.is_default = validated_data.get("is_default", instance.is_default)

        instance.updated_by = self.context.get("user")
        instance.updated_at = datetime.datetime.now()
        instance.save()
        return instance

    def validate(self, data):
        status_type = data.get('status_type') 
     
        if not status_type and self.instance:
            status_type = self.instance.status_type

        if 'weight' not in data and status_type:
            data['weight'] = self.STATUS_WEIGHTS.get(status_type.lower(), 0)
            
        
        name = str(data.get("name", "")).strip()
        code = str(data.get("code", "")).strip()

        # Name uniqueness
        qs_name = TicketStatus.objects.filter(name__iexact=name)
        if self.instance:
            qs_name = qs_name.exclude(reference_id=self.instance.reference_id)
        if qs_name.exists():
            raise serializers.ValidationError(
                {
                    global_parameters.ERROR_DETAILS: [
                        f"Ticket status with name '{name}' already exists."
                    ]
                }
            )

        # Code uniqueness
        qs_code = TicketStatus.objects.filter(code__iexact=code)
        if self.instance:
            qs_code = qs_code.exclude(reference_id=self.instance.reference_id)
        if qs_code.exists():
            raise serializers.ValidationError(
                {
                    global_parameters.ERROR_DETAILS: [
                        f"Ticket status with code '{code}' already exists."
                    ]
                }
            )

        data["name"] = name
        data["code"] = code.upper()
        return data


class TicketStatusListSerializer(serializers.Serializer):
    referenceId = serializers.CharField(source="reference_id", read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    statusType = serializers.CharField(read_only=True, source="status_type")
    isDefault = serializers.BooleanField(read_only=True, source="is_default")
    weight = serializers.IntegerField(read_only=True)
