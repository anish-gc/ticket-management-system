# accounts/management/commands/grant_admin_menu_permissions.py

from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Role, Menu, RoleMenuPermission


class Command(BaseCommand):
    help = "Grant the admin role all menu permissions (full CRUD)."

    def handle(self, *args, **options):
        try:
            admin_role = Role.objects.get(name="admin")
        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Admin role does not exist."))
            return

        menus = Menu.objects.filter(is_active=True)
        if not menus.exists():
            self.stdout.write(self.style.WARNING("⚠️ No menus found."))
            return

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for menu in menus:
                perm, created = RoleMenuPermission.objects.update_or_create(
                    role=admin_role,
                    menu=menu,
                    defaults={
                        "can_create": True,
                        "can_view": True,
                        "can_update": True,
                        "can_delete": True,
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Admin role now has full permissions for all menus "
                f"(Created: {created_count}, Updated: {updated_count})."
            )
        )
