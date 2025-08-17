from django.db import models
from django.utils.translation import gettext_lazy as _


from utilities.exception import CustomAPIException
from utilities.models import BaseModel


class Role(BaseModel):
    """
    Role model for managing user permissions and access control.
    """

    name = models.CharField(
        _("name"), max_length=150, help_text=_("The name of the role"), unique=True,db_index=True,  
    )

    is_predefined = models.BooleanField(
        default=False, help_text=_("Whether this role is predefined by the system")
    )

    class Meta:
        db_table = "roles"
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_predefined", "name"]), 
        ]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Role: {self.name}>"

    def can_be_deleted(self) -> bool:
        """
        Check if this role can be safely deleted.
        Predefined roles typically shouldn't be deleted.

        Returns:
            bool: True if the role can be deleted
        """
        return not self.is_predefined

    @classmethod
    def get_default_roles(cls):
        """Get all predefined/default roles."""
        return cls.objects.predefined()

    def ensure_not_predefined(self):
        if self.is_predefined:
            raise CustomAPIException("You cannot modify or delete default roles...")
