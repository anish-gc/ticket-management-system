from utilities.models import BaseModel
from django.db import models
import datetime


class Ticket(BaseModel):
    """Main ticket model"""

    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    menu = models.ForeignKey(
        "accounts.Menu",  
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Menu/module this ticket relates to",
    )
    # Status and Priority
    status = models.ForeignKey("tickets.TicketStatus", on_delete=models.PROTECT)
    priority = models.ForeignKey("tickets.TicketPriority", on_delete=models.PROTECT)

    # User relationships

    created_for = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_received",
    )

    assigned_to = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    first_response_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when staff first responded to the ticket"
    )
    # Deadlines
    response_deadline = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)  # resolution deadline
    resolved_at = models.DateTimeField(null=True, blank=True)

    # SLA tracking
    sla_due_date = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False)
    is_escalated = models.BooleanField(default=False, db_index=True)

    # Feedback
    customer_satisfaction = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        null=True,
        blank=True,
        help_text="Customer satisfaction rating 1-5",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            today = datetime.date.today()
            count = Ticket.objects.filter(created_at__date=today).count() + 1
            self.ticket_number = f"TKT-{today.strftime('%Y%m%d')}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"
