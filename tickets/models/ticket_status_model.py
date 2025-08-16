from django.db import models

from utilities.models import BaseModel

class TicketStatus(BaseModel):
    """Dynamic ticket status with weight for sorting"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    weight = models.IntegerField(default=0, help_text="Lower weight = higher priority in sorting")
    
    # Status type for business logic
    STATUS_TYPE_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    status_type = models.CharField(max_length=20, choices=STATUS_TYPE_CHOICES)
    
    is_default = models.BooleanField(default=False, help_text="Default status for new tickets")
  
    
    class Meta:
        ordering = ['weight', 'name']
        verbose_name = "Ticket Status"
        verbose_name_plural = "Ticket Statuses"
        db_table = 'ticket_status'
    
    def __str__(self):
        return self.name