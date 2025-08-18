from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db import transaction

from accounts.models.menu_model import Menu

User = get_user_model()


# Basic usage
# python manage.py load_menu_structure

# Clear existing menus and reload
# python manage.py load_menu_structure --clear

# Use custom admin credentials
# python manage.py load_menu_structure --admin-username=superadmin --admin-email=admin@yoursite.com

# Combine options
# python manage.py load_menu_structure --clear --admin-username=myuser

class Command(BaseCommand):
    help = 'Loads the complete menu structure into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing menu items before loading new ones',
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username for admin user (default: admin)',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@example.com',
            help='Email for admin user (default: admin@example.com)',
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Clear existing menus if requested
                if options['clear']:
                    deleted_count = Menu.objects.all().count()
                    Menu.objects.all().delete()
                    self.stdout.write(
                        self.style.WARNING(f'Cleared {deleted_count} existing menu items')
                    )

                # Ensure admin user exists
                admin_user = self.get_or_create_admin_user(
                    options['admin_username'],
                    options['admin_email']
                )

                # Menu data from your database snapshot
                menu_data = [
                    {
                        "reference_id": "c6df6120f59c46a1bc09eaae6286fc34",
                        "menu_name": "Account Management",
                        "menu_url": "#",
                        "create_url": "#",
                        "list_url": "#",
                        "parent_ref": None,
                        "display_order": 1,
                        "depth": 0,
                    },
                    {
                        "reference_id": "ba5e5ebc6887410e8352039d02acf744",
                        "menu_name": "Accounts",
                        "menu_url": "/accounts/",
                        "create_url": "/accounts/create/",
                        "list_url": "/accounts/list/",
                        "parent_ref": "c6df6120f59c46a1bc09eaae6286fc34",
                        "display_order": 1,
                        "depth": 1,
                    },
                    {
                        "reference_id": "485dee4c021149168ce274f7d23c8695",
                        "menu_name": "Roles",
                        "menu_url": "/roles/",
                        "create_url": "/roles/create/",
                        "list_url": "/roles/list/",
                        "parent_ref": "c6df6120f59c46a1bc09eaae6286fc34",
                        "display_order": 2,
                        "depth": 1,
                    },
                    {
                        "reference_id": "c4f94146aad6453fbfc690dc77d1193b",
                        "menu_name": "Mapping",
                        "menu_url": "#",
                        "create_url": "#",
                        "list_url": "#",
                        "parent_ref": None,
                        "display_order": 2,
                        "depth": 0,
                    },
                    {
                        "reference_id": "f14b42987caa46b189fa69bb5b54f300",
                        "menu_name": "Account Role Mapping",
                        "menu_url": "/account/role/mapping/",
                        "create_url": "/account/role/mapping/create/",
                        "list_url": "/account/role/mapping/list/",
                        "parent_ref": "c4f94146aad6453fbfc690dc77d1193b",
                        "display_order": 1,
                        "depth": 1,
                    },
                    {
                        "reference_id": "6d0de2bc3cd34389b7f921eed1458847",
                        "menu_name": "Role Menu Permission Mapping",
                        "menu_url": "/role/menu/permission/mapping/",
                        "create_url": "/role/menu/permission/mapping/create/",
                        "list_url": "/role/menu/permission/mapping/list/",
                        "parent_ref": "c4f94146aad6453fbfc690dc77d1193b",
                        "display_order": 2,
                        "depth": 1,
                    },
                    {
                        "reference_id": "ddc297800dab427fbda4f47a7d4cfb34",
                        "menu_name": "Account Menu Mapping",
                        "menu_url": "/account/menu/mapping/",
                        "create_url": "/account/menu/mapping/create/",
                        "list_url": "/account/menu/mapping/list/",
                        "parent_ref": "c4f94146aad6453fbfc690dc77d1193b",
                        "display_order": 3,
                        "depth": 1,
                    },
                    {
                        "reference_id": "b259bb4434f743e8ba8f3022274b2fde",
                        "menu_name": "Ticket Management",  # Fixed typo
                        "menu_url": "#",
                        "create_url": "#",
                        "list_url": "#",
                        "parent_ref": None,
                        "display_order": 3,
                        "depth": 0,
                    },
                    {
                        "reference_id": "6f93380923f74ad5829ae69d11646668",
                        "menu_name": "Tickets",
                        "menu_url": "/tickets/",
                        "create_url": "/tickets/create/",
                        "list_url": "/tickets/list/",
                        "parent_ref": "b259bb4434f743e8ba8f3022274b2fde",
                        "display_order": 1,
                        "depth": 1,
                    },
                    {
                        "reference_id": "0d23631999754eb7b41824dfd4a01964",
                        "menu_name": "Ticket Status",  # Fixed typo
                        "menu_url": "/ticket-status/",
                        "create_url": "/ticket-status/create/",
                        "list_url": "/ticket-status/list/",
                        "parent_ref": "b259bb4434f743e8ba8f3022274b2fde",
                        "display_order": 2,
                        "depth": 1,
                    },
                    {
                        "reference_id": "19f9cd9e06824eb68b08d73459180b62",
                        "menu_name": "Ticket Priority",
                        "menu_url": "/ticket-priority/",
                        "create_url": "/ticket-priority/create/",
                        "list_url": "/ticket-priority/list/",
                        "parent_ref": "b259bb4434f743e8ba8f3022274b2fde",
                        "display_order": 3,
                        "depth": 1,
                    },
                    {
                        "reference_id": "392fa89e362e47dc9560841975f34fed",
                        "menu_name": "Notification Log",
                        "menu_url": "/tickets/notification-logs/",
                        "create_url": "/tickets/notification-logs/create/",
                        "list_url": "/tickets/notification-logs/list/",
                        "parent_ref": "b259bb4434f743e8ba8f3022274b2fde",
                        "display_order": 4,
                        "depth": 1,
                    },
                ]

                # Load menu items
                created_menus = self.load_menu_items(menu_data, admin_user)
                
                # Set parent relationships
                self.set_parent_relationships(menu_data, created_menus)

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully loaded {len(menu_data)} menu items')
                )

        except Exception as e:
            raise CommandError(f'Failed to load menu structure: {str(e)}')

    def get_or_create_admin_user(self, username, email):
        """Get or create admin user"""
        try:
            admin_user = User.objects.get(id=1)
            self.stdout.write(
                self.style.NOTICE(f'Using existing admin user: {admin_user.username}')
            )
        except User.DoesNotExist:
            try:
                # Try to get by username first
                admin_user = User.objects.get(username=username)
                self.stdout.write(
                    self.style.NOTICE(f'Using existing user: {admin_user.username}')
                )
            except User.DoesNotExist:
                admin_user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password='admin123'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created admin user: {username}')
                )
        return admin_user

    def load_menu_items(self, menu_data, admin_user):
        """Create or update menu items"""
        created_menus = {}
        
        for item in menu_data:
            defaults = {
                'menu_name': item['menu_name'],
                'menu_url': item['menu_url'],
                'create_url': item['create_url'],
                'list_url': item['list_url'],
                'icon': '',
                'visibility': True,
                'display_order': item['display_order'],
                'depth': item['depth'],
                'is_active': True,
                'remarks': '',
                'created_by': admin_user,
                'updated_by': admin_user,
                'created_at': now(),
                'updated_at': now(),
            }
            
            menu, created = Menu.objects.update_or_create(
                reference_id=item['reference_id'],
                defaults=defaults
            )
            
            created_menus[item['reference_id']] = menu
            
            status = self.style.SUCCESS('CREATED') if created else self.style.NOTICE('UPDATED')
            self.stdout.write(f"{status} Menu: {menu.menu_name}")
            
        return created_menus

    def set_parent_relationships(self, menu_data, created_menus):
        """Set parent-child relationships for menu items"""
        for item in menu_data:
            if item['parent_ref']:
                try:
                    menu = created_menus[item['reference_id']]
                    parent = created_menus.get(item['parent_ref'])
                    
                    if parent:
                        menu.parent = parent
                        menu.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Set parent: {menu.menu_name} → {parent.menu_name}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Parent not found for {menu.menu_name} "
                                f"(parent_ref: {item['parent_ref']})"
                            )
                        )
                        
                except KeyError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Menu not found in created_menus: {e}"
                        )
                    )