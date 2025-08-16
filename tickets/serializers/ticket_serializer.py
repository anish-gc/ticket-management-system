from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models.menu_model import Menu
from utilities.global_functions import model_validation


class TicketSerializer(serializers.Serializer):

    # Required fields
    title = serializers.CharField(
        max_length=200,
        error_messages={
            "required": "Ticket title is required.",
            "blank": "Ticket title cannot be blank.",
            "max_length": "Title cannot exceed 200 characters.",
        },
    )

    description = serializers.CharField(
        error_messages={
            "required": "Ticket description is required.",
            "blank": "Ticket description cannot be blank.",
        }
    )

    menuId = serializers.CharField(
        source="menu",
        allow_null=True,
        required=False,
    )

    statusId = serializers.CharField(
        source="status",
        error_messages={
            "required": "Status is required.",
        },
    )

    priorityId = serializers.CharField(
        source="priority",
        error_messages={
            "required": "Priority is required.",
        },
    )

    createdFor = serializers.CharField(
        source="created_for",
        allow_null=True,
        required=False,
    )

    assignedTo = serializers.CharField(
        source="assigned_to",
        allow_null=True,
        required=False,
    )

    responseDeadline = serializers.CharField(
        required=False,
        allow_null=True,
        source="response_deadline",
    )

    dueDate = serializers.CharField(
        required=False,
        allow_null=True,
        source="due_date",
    )

    resolvedAt = serializers.CharField(
        required=False,
        allow_null=True,
        source="resolved_at",
    )

    slaDueDate = serializers.CharField(
        required=False,
        allow_null=True,
        source="sla_due_date",
    )

    # Boolean fields
    slaBreached = serializers.BooleanField(
        required=False, default=False, source="sla_breached"
    )

    isEscalated = serializers.BooleanField(
        required=False, default=False, source="is_escalated"
    )

    # Customer satisfaction with validation
    customerSatisfaction = serializers.IntegerField(
        required=False,
        allow_null=True,
        source="customer_satisfaction",
        validators=[
            MinValueValidator(
                1, message="Customer satisfaction rating must be between 1 and 5."
            ),
            MaxValueValidator(
                5, message="Customer satisfaction rating must be between 1 and 5."
            ),
        ],
        error_messages={
            "invalid": "Enter a valid integer for customer satisfaction rating."
        },
    )

    def validate(self, data):
        menu_reference_id = data.get('menuId')
        menu = model_validation(Menu, 'Select a valid menu', {'reference_id': menu_reference_id})
        


#     def validate(self, data):
#         """Cross-field validation"""
#         errors = {}

#         # Validate that due_date is after response_deadline if both are provided
#         if data.get("due_date") and data.get("response_deadline"):
#             if data["due_date"] <= data["response_deadline"]:
#                 errors["dueDate"] = "Due date must be after response deadline."

#         # Validate that resolved_at is provided when status indicates resolution
#         # (You'll need to implement this based on your status logic)

#         if errors:
#             raise serializers.ValidationError(errors)

#         return data

#     def validate_customerSatisfaction(self, value):
#         """Additional validation for customer satisfaction"""
#         if value is not None and value not in range(1, 6):
#             raise serializers.ValidationError(
#                 "Customer satisfaction rating must be between 1 and 5."
#             )
#         return value


# # Usage example in your view:
# # serializer = TicketSerializer(
# #     data=request.data,
# #     context={
# #         'menu_queryset': Menu.objects.all(),
# #         'status_queryset': TicketStatus.objects.all(),
# #         'priority_queryset': TicketPriority.objects.all(),
# #         'account_queryset': Account.objects.all(),
# #     }
# # )


class TicketListSerializer(serializers.Serializer):
    """Read-only serializer for Ticket"""

    referenceId = serializers.CharField(source="referenceId", read_only=True)
    ticketNumber = serializers.CharField(source="ticket_number", read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    # Expand related fields into human-readable values
    menu = serializers.CharField(source="menu.menu_name", read_only=True)
    status = serializers.CharField(source="status.name", read_only=True)
    priority = serializers.CharField(source="priority.name", read_only=True)
    createdFor = serializers.CharField(source="created_for.username", read_only=True)
    assignedTo = serializers.CharField(source="assigned_to.username", read_only=True)

    responseDeadline = serializers.DateTimeField(
        source="response_deadline", read_only=True
    )
    dueDate = serializers.DateTimeField(source="due_date", read_only=True)
    resolvedAt = serializers.DateTimeField(source="resolved_at", read_only=True)
    slaDueDate = serializers.DateTimeField(source="sla_due_date", read_only=True)

    slaBreached = serializers.BooleanField(source="sla_breached", read_only=True)
    isEscalated = serializers.BooleanField(source="is_escalated", read_only=True)

    customerSatisfaction = serializers.IntegerField(
        source="customer_satisfaction", read_only=True
    )

    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
