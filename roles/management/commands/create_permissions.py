from django.core.management.base import BaseCommand
from roles.models import Permission

class Command(BaseCommand):
    help = 'Create initial permissions'

    def handle(self, *args, **options):
        permissions = [
            ('VIEW_COMPANIES', 'Can view companies'),
            ('CREATE_COMPANY', 'Can create companies'),
            ('UPDATE_COMPANY', 'Can update companies'),
            ('DELETE_COMPANY', 'Can delete companies'),
            ('VIEW_USERS', 'Can view users'),
            ('CREATE_USER', 'Can create users'),
            ('UPDATE_USER', 'Can update users'),
            ('DELETE_USER', 'Can delete users'),
            ('VIEW_ROLES', 'Can view roles'),
            ('CREATE_ROLE', 'Can create roles'),
            ('UPDATE_ROLE', 'Can update roles'),
            ('DELETE_ROLE', 'Can delete roles'),
            ('VIEW_PERMISSIONS', 'Can view permissions'),
            ('ASSIGN_PERMISSIONS', 'Can assign permissions to roles'),
            ('ASSIGN_ROLES', 'Can assign roles to users'),
            ('VIEW_AUDIT_LOGS', 'Can view audit logs'),
        ]

        for name, description in permissions:
            permission, created = Permission.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'Created permission: {name}')
            else:
                self.stdout.write(f'Permission already exists: {name}')

        self.stdout.write(self.style.SUCCESS('Successfully created permissions'))