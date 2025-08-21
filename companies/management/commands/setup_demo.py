from django.core.management.base import BaseCommand
from companies.models import Company, User
from roles.models import Role, Permission, UserRole

class Command(BaseCommand):
    help = 'Setup demo data with company and admin user'

    def handle(self, *args, **options):
        # Create demo company
        company, created = Company.objects.get_or_create(
            name='Demo Company',
            defaults={'description': 'Demo company for testing'}
        )
        
        if created:
            self.stdout.write(f'Created company: {company.name}')
        
        # Create admin role with all permissions
        admin_role, created = Role.objects.get_or_create(
            name='Admin',
            company=company,
            defaults={'description': 'Full system administrator'}
        )
        
        if created:
            # Assign all permissions to admin role
            permissions = Permission.objects.all()
            admin_role.permissions.set(permissions)
            self.stdout.write(f'Created admin role with {permissions.count()} permissions')
        
        # Create demo admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@demo.com',
                'company': company,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
            # Assign admin role to user
            UserRole.objects.get_or_create(user=admin_user, role=admin_role)
            
            self.stdout.write(f'Created admin user: {admin_user.username}')
            self.stdout.write('Password: admin123')
        
        self.stdout.write(self.style.SUCCESS('Demo setup completed successfully'))