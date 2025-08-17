

from utilities.models import BaseModel
from django.db import models

class TicketPriority(BaseModel):
    """Dynamic ticket priority with weight for sorting and SLA configuration"""
    name = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Display name of the priority level"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Short code for programmatic reference"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed explanation of this priority level"
    )
    weight = models.IntegerField(
        default=0,
        db_index=True,
        help_text="Higher weight = higher priority (used for sorting)",
       
    )
    color = models.CharField(
        max_length=7,
        default="#28a745",
        help_text="Hex color code for UI display (e.g., #28a745)"
    )
    sla_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="SLA response time in hours (leave blank for no SLA)"
    )
    is_default = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Default priority for new tickets (only one priority can be default)"
    )
    class Meta:
        ordering = ['-weight', 'name']
        verbose_name = "Ticket Priority"
        verbose_name_plural = "Ticket Priorities"
        db_table = 'ticket_priorities'
        indexes = [
            models.Index(fields=['weight', 'is_default']),
            models.Index(fields=['sla_hours', 'is_default']),
        ]
    
    def __str__(self):
        return self.name