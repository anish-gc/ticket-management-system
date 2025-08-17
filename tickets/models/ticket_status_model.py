from django.db import models

from utilities.models import BaseModel

class TicketStatus(BaseModel):
    """Dynamic ticket status with categorization and weighted sorting"""
    name = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Display name of the status (e.g., 'Open', 'In Progress')"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Short code for programmatic reference (e.g., 'OPEN')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed explanation of this status and when it should be used"
    )
    weight = models.IntegerField(
        default=0,
        db_index=True,
        help_text="Lower weight = higher priority in sorting (0=highest priority)"
    )
    
    STATUS_TYPE_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    status_type = models.CharField(
        max_length=20,
        choices=STATUS_TYPE_CHOICES,
        db_index=True,
        help_text="Business classification of this status"
    )
    
    is_default = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Default status for new tickets (only one status can be default)"
    )
    
    class Meta:
        ordering = ['weight', 'name']
        verbose_name = "Ticket Status"
        verbose_name_plural = "Ticket Statuses"
        db_table = 'ticket_status'
        indexes = [
            models.Index(fields=['status_type', 'weight']),  
            models.Index(fields=['is_default', 'weight']),  
        ]
    
    def __str__(self):
        return self.name