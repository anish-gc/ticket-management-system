from django.db import models

from utilities.models import BaseModel


class NotificationLog(BaseModel):
    """System-wide notification logging with delivery tracking"""

    NOTIFICATION_TYPE_CHOICES = [
        ("ticket_created", "Ticket Created"),
        ("ticket_updated", "Ticket Updated"),
        ("ticket_assigned", "Ticket Assigned"),
        ("ticket_reassigned", "Ticket Reassigned"),
        ("status_changed", "Status Changed"),
        ("priority_changed", "Priority Changed"),
        ("due_date_approaching", "Due Date Approaching"),
    ]

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        db_index=True,
        help_text="Type/category of the notification",
    )
    recipient = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
        help_text="User receiving the notification",
    )
    sender = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
        db_index=True,
        help_text="User/system that triggered the notification",
    )
    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
        help_text="Related ticket (if applicable)",
    )

    title = models.CharField(
        max_length=200, help_text="Short summary of the notification"
    )
    message = models.TextField(help_text="Full content of the notification")

    # Delivery status tracking
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether recipient has viewed the notification",
    )
    is_sent = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether notification was successfully delivered",
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Timestamp when notification was delivered",
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Timestamp when recipient viewed the notification",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        db_table = 'notification_log'
        indexes = [
            # Existing indexes
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["notification_type"]),
            # New recommended indexes
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["is_sent", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
            models.Index(fields=["is_read", "is_sent"]),
            # Partial index for unread notifications
            models.Index(
                fields=["recipient"],
                name="unread_notifications_idx",
                condition=models.Q(is_read=False),
            ),
        ]

    @property
    def delivery_latency(self):
        """Time between creation and sending"""
        if self.sent_at and self.created_at:
            return self.sent_at - self.created_at
        return None

    @property
    def read_latency(self):
        """Time between sending and reading"""
        if self.read_at and self.sent_at:
            return self.read_at - self.sent_at
        return None

    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.recipient} ({'read' if self.is_read else 'unread'})"
