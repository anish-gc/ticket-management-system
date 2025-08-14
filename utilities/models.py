import logging
from django.db import models
from django.conf import settings
from typing import TypeVar, Optional, Type

from utilities.global_functions import generate_uuid

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="BaseModel")


class BaseModel(models.Model):
    """
    Abstract base model for all models in the project.
    Provides common fields and methods with robust error handling.
    """

    id = models.BigAutoField(primary_key=True, null=False, unique=True)

    reference_id = models.CharField(
        max_length=32,
        unique=True,
        null=False,
        default=generate_uuid,
        editable=False,
        db_index=True,
        help_text="Unique identifier for external reference",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_created",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    # Status fields with composite index consideration
    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Status to check if the entity is active"
    )

    remarks = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            # Composite indexes for common query patterns
            models.Index(fields=["is_active", "created_at"]),
            models.Index(fields=["created_by", "is_active"]),
        ]

    @classmethod
    def get_by_reference_id(cls: Type[T], reference_id: str) -> Optional[T]:
        """
        Get an object by its reference_id.

        Args:
            reference_id: The reference ID to search for

        Returns:
            The object if found, None otherwise
        """
        try:
            return cls.objects.get(reference_id=reference_id)
        except cls.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error retrieving {cls.__name__} by reference_id: {e}")
            return None

    def save(self, *args, **kwargs):
        """Override save to add validation and optimization."""
        # Run validation
        self.full_clean()

        # Optimize update_fields if not provided
        if "update_fields" not in kwargs and self.pk:
            # Only update changed fields for existing objects
            original = self.__class__.objects.filter(pk=self.pk).first()
            if original:
                changed_fields = []
                for field in self._meta.fields:
                    if getattr(self, field.name) != getattr(original, field.name):
                        changed_fields.append(field.name)

                # Always include updated_at for tracking
                if "updated_at" not in changed_fields:
                    changed_fields.append("updated_at")

                if changed_fields:
                    kwargs["update_fields"] = changed_fields

        super().save(*args, **kwargs)
