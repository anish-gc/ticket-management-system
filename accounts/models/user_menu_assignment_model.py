

from accounts.models.account_model import Account
from django.db import models

from utilities.models import BaseModel

class UserMenuAssignment(BaseModel):
    """Assign specific menu sets to users"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='menu_assignments')
    menu = models.ForeignKey('accounts.Menu', on_delete=models.CASCADE, null=True, blank=True)
    assigned_by = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, null=True, related_name='menu_assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    can_view = models.BooleanField(default=True)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    class Meta:
        db_table = "user_menu_assignments"
        verbose_name = "User Menu Assignment"
        verbose_name_plural = "User Menu Assignments"
        ordering = ["-assigned_at"]
        constraints = [
            models.UniqueConstraint(
                fields=['account', 'menu'],
                name='unique_user_menu_assignment',
                condition=models.Q(menu__isnull=False)
            )
        ]
        indexes = [
            models.Index(fields=['account', 'assigned_at']),
            models.Index(fields=['menu', 'assigned_at']),
            models.Index(fields=['assigned_by']),
        ]