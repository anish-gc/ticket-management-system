

from utilities.models import BaseModel
from django.db import models

class TicketPriority(BaseModel):
    """Dynamic ticket priority with weight for sorting"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    weight = models.IntegerField(default=0, help_text="Higher weight = higher priority")
    color = models.CharField(max_length=7, default="#28a745", help_text="Hex color code for UI")
    
    # SLA settings
    sla_hours = models.PositiveIntegerField(null=True, blank=True, help_text="SLA response time in hours")
    
    is_default = models.BooleanField(default=False, help_text="Default priority for new tickets")
    
    class Meta:
        ordering = ['-weight', 'name']
        verbose_name = "Ticket Priority"
        verbose_name_plural = "Ticket Priorities"
        db_table = 'ticket_priorities'
    
    def __str__(self):
        return self.name