

from accounts.models.account_model import Account
from django.db import models

class UserMenuAssignment(models.Model):
    """Assign specific menu sets to users"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='menu_assignments')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='menu_assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]