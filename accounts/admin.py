from django.contrib import admin
from .models import Menu

from accounts.models import RoleMenuPermission


from .models import Role
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = (
        "reference_id",
        "username",
        "email",
        "phone_number",
        "role",
        "is_active",
        "is_staff",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "is_staff", "role")
    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("email", "phone_number", "address", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login",  )}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "role",
                ),
            },
        ),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("reference_id", "name", "is_predefined")
    list_filter = ("is_predefined",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        "reference_id",
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


@admin.register(RoleMenuPermission)
class RoleMenuPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "reference_id",
        "role",
        "menu",
        "can_create",
        "can_view",
        "can_update",
        "can_delete",
        "created_at",
        "updated_at",
    )
    list_filter = ("role", "menu", "can_create", "can_view", "can_update", "can_delete")
    search_fields = ("role__name", "menu__menu_name")
    ordering = ("role", "menu")
