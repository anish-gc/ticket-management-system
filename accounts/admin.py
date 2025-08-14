from django.contrib import admin
from .models import Menu

from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_predefined")
    list_filter = ("is_predefined",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        "menu_name",
        "menu_url",
        "parent",
        "visibility",
        "display_order",
        "depth",
    )
    list_filter = ("visibility", "parent")
    search_fields = ("menu_name", "menu_url", "create_url", "list_url")
    ordering = ("display_order", "menu_name")
    autocomplete_fields = ("parent",)
