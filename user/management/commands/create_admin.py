from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create superuser for InnovaSus if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('ℹ️  Superuser already exists')
            )
            return
        
        # Create superuser only if CREATE_SUPERUSER is true
        if os.environ.get('CREATE_SUPERUSER', '').lower() == 'true':
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
                self.style.WARNING('ℹ️  CREATE_SUPERUSER not enabled')
            )