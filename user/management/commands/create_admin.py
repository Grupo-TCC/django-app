from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create superuser for InnovaSus if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        create_superuser_env = os.environ.get('CREATE_SUPERUSER', '')
        self.stdout.write(f'🔍 CREATE_SUPERUSER environment variable: "{create_superuser_env}"')
        
        # Check if any superuser exists
        existing_superusers = User.objects.filter(is_superuser=True)
        if existing_superusers.exists():
            self.stdout.write(
                self.style.WARNING(f'ℹ️  Superuser already exists: {[u.email for u in existing_superusers]}')
            )
            return
        
        # Create superuser only if CREATE_SUPERUSER is true
        if create_superuser_env.lower() == 'true':
            try:
                admin_user = User.objects.create_superuser(
                    email='admin@innovasus.com',
                    password='InnovaAdmin2025!',
                    fullname='Admin User'
                )
                # Ensure the user is active and verified
                admin_user.is_active = True
                admin_user.email_verified = True
                admin_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Superuser created successfully: admin@innovasus.com')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creating superuser: {e}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'ℹ️  CREATE_SUPERUSER not enabled. Value: "{create_superuser_env}"')
            )