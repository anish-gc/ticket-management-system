from rest_framework import serializers

from accounts.models.account_model import Account
from accounts.models.menu_model import Menu
from tickets.models.ticket_model import Ticket
from tickets.models.ticket_priority_model import TicketPriority
from tickets.models.ticket_status_model import TicketStatus
from utilities.exception import CustomAPIException
from utilities.global_functions import model_validation, validate_datetime
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator


class TicketSerializer(serializers.Serializer):
    # Required fields
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()

    # Foreign keys via reference IDs
    menuId = serializers.CharField(source="menu", allow_null=True, required=False)
    statusId = serializers.CharField(source="status")
    priorityId = serializers.CharField(source="priority")
    createdFor = serializers.CharField(
        source="created_for", allow_null=True, required=False
    )
    assignedTo = serializers.CharField(
        source="assigned_to", allow_null=True, required=False
    )

    # Datetime fields (strings from API, converted internally)
    responseDeadline = serializers.CharField(
        source="response_deadline", allow_null=True, required=False
    )
    dueDate = serializers.CharField(source="due_date", allow_null=True, required=False)
    resolvedAt = serializers.CharField(
        source="resolved_at", allow_null=True, required=False
    )
    slaDueDate = serializers.CharField(
        source="sla_due_date", allow_null=True, required=False
    )

    # Booleans
    slaBreached = serializers.BooleanField(
        source="sla_breached", default=False, required=False
    )
    isEscalated = serializers.BooleanField(
        source="is_escalated", default=False, required=False
    )

    # Customer satisfaction
    customerSatisfaction = serializers.IntegerField(
        source="customer_satisfaction",
        required=False,
        allow_null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    def validate(self, data):
        """
        Validate reference IDs, parse datetime strings, and apply business logic
        """
        self._resolve_foreign_keys(data)
        self._parse_datetime_fields(data)
        self._validate_deadline_order(data)
        self._apply_business_logic(data)
        return data

    def _resolve_foreign_keys(self, data):
        fk_mapping = {
            "menu": Menu,
            "status": TicketStatus,
            "priority": TicketPriority,
            "created_for": Account,
            "assigned_to": Account,
        }
        for field, model in fk_mapping.items():
            ref_id = data.get(field)
            if ref_id:
                data[field] = model_validation(
                    model, f"Select a valid {field}", {"reference_id": ref_id}
                )

    def _parse_datetime_fields(self, data):
        datetime_fields = [
            "response_deadline",
            "due_date",
            "resolved_at",
            "sla_due_date",
        ]
        for field in datetime_fields:
            if field in data and data[field] is not None:
                # Parse string to aware datetime
                data[field] = validate_datetime(data[field])

    def _validate_deadline_order(self, data):
        rd = data.get("response_deadline")
        dd = data.get("due_date")
        if rd and dd and dd <= rd:
            raise CustomAPIException("Due date must be after response deadline.")

    def _apply_business_logic(self, data):
        """
        Auto-set SLA, first_response_at, and calculate SLA breach
        """
        request = self.context.get("request")
        instance = getattr(self, "instance", None)

        # Auto SLA due date
        if data.get("priority") and not data.get("sla_due_date"):
            sla_hours = getattr(data["priority"], "sla_hours", None)
            if sla_hours:
                data["sla_due_date"] = timezone.now() + timedelta(hours=sla_hours)

        # First response timestamp
        if instance and request and hasattr(request, "user") and request.user.is_staff:
            if not getattr(instance, "first_response_at", None):
                data["first_response_at"] = timezone.now()

        # SLA breached calculation
        first_response = data.get("first_response_at")
        sla_due = data.get("sla_due_date")
        if first_response and sla_due:
            data["sla_breached"] = first_response > sla_due
        elif "sla_breached" not in data:
            data["sla_breached"] = False

    def create(self, validated_data):
        return Ticket.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TicketListSerializer(serializers.Serializer):
    """Read-only serializer for Ticket"""

    referenceId = serializers.CharField(source="reference_id", read_only=True)
    ticketNumber = serializers.CharField(source="ticket_number", read_only=True)

    # Human-readable relations
    menu = serializers.CharField(source="menu.menu_name", read_only=True)
    status = serializers.CharField(source="status.name", read_only=True)
    priority = serializers.CharField(source="priority.name", read_only=True)
    createdFor = serializers.CharField(source="created_for.username", read_only=True)
    assignedTo = serializers.CharField(source="assigned_to.username", read_only=True)

    # DateTime fields
    responseDeadline = serializers.DateTimeField(
        source="response_deadline", read_only=True
    )
    dueDate = serializers.DateTimeField(source="due_date", read_only=True)
    resolvedAt = serializers.DateTimeField(source="resolved_at", read_only=True)
    slaDueDate = serializers.DateTimeField(source="sla_due_date", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    # Flags and ratings
    slaBreached = serializers.BooleanField(source="sla_breached", read_only=True)
    isEscalated = serializers.BooleanField(source="is_escalated", read_only=True)
    customerSatisfaction = serializers.IntegerField(
        source="customer_satisfaction", read_only=True
    )
