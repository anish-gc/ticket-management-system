from django.db import models
from utilities.models import BaseModel

class Menu(BaseModel):
    """
    Model representing a navigational menu item.
    """
    menu_name = models.CharField(max_length=200, help_text="Display name of the menu")
    menu_url = models.CharField(max_length=200, help_text="URL to access the menu")
    create_url = models.CharField(max_length=200, blank=True, null=True, help_text="URL for creating a new item")
    list_url = models.CharField(max_length=200, blank=True, null=True, help_text="URL to list all items")
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent menu item, if this is a sub-menu"
    )
    icon = models.CharField(max_length=100, null=True, blank=True, help_text="Icon class or path")
    visibility = models.BooleanField(default=True, help_text="Whether this menu is visible")
    display_order = models.IntegerField(default=0, help_text="Order to display menus")
    depth = models.PositiveIntegerField(default=0, help_text="Depth level of the menu for nested menus")

    class Meta:
        db_table = "menus"
        ordering = ["display_order", "menu_name"]
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    def __str__(self):
        return self.menu_name




