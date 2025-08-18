from django.core.management.base import BaseCommand
from accounts.models.account_model import Account
from accounts.models.role_model import Role


class Command(BaseCommand):
    help = "Create predefined roles (Admin, Supervisor, Agent, Customer)"

    def handle(self, *args, **kwargs):
        predefined_roles = [
            {"name": "admin", "description": "System administrator"},
            {"name": "supervisor", "description": "Ticket supervisor"},
            {"name": "agent", "description": "Support agent"},
            {"name": "customer", "description": "End user / customer"},
        ]

        superuser = Account.objects.filter(is_superuser=True).first()

        for role_data in predefined_roles:
            role, created = Role.objects.get_or_create(
                name=role_data["name"].lower(),  # 👈 use `name` as lookup
                defaults={
                    "is_predefined": True,
                    "created_by": superuser,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created role: {role.name}"))
            else:
                if not role.is_predefined:
                    role.is_predefined = True
                    role.save(update_fields=["is_predefined"])
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ Updated role: {role.name} to predefined")
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(f"ℹ️ Role already exists: {role.name}")
                    )
