from django.core.management.base import BaseCommand
from companies.models import User
from roles.models import Permission

class Command(BaseCommand):
    help = 'Create superuser with dashboard access'

    def handle(self, *args, **options):
        # Create superuser if doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser created: {superuser.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists')
            )