from django.db import models
from utilities.models import BaseModel


class RoleMenuPermission(BaseModel):
    """
    Model representing permissions a role has on a specific menu.
    """
    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.PROTECT,
        related_name="menu_permissions",
        help_text="Role assigned to this permission"
    )
    menu = models.ForeignKey(
        "accounts.Menu",
        on_delete=models.PROTECT,
        related_name="role_permissions",
        help_text="Menu for which the role has permissions"
    )
    can_create = models.BooleanField(default=False, help_text="Whether the role can create items in this menu")
    can_view = models.BooleanField(default=False, help_text="Whether the role can view this menu")
    can_update = models.BooleanField(default=False, help_text="Whether the role can update items in this menu")
    can_delete = models.BooleanField(default=False, help_text="Whether the role can delete items in this menu")

    class Meta:
        db_table = "role_menu_permission"
        verbose_name = "Role Menu Permission"
        verbose_name_plural = "Role Menu Permissions"
        unique_together = ("role", "menu")
        ordering = ["role_id", "menu_id"]

    def __str__(self):
        return f"{self.role} permissions for {self.menu}"
