#!/bin/bash

# InnovaSus Render.com Pre-Deploy Script
# This runs before the server starts
echo "🌟 InnovaSus Pre-Deploy Tasks..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"setup.settings_render"}

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE

# Create superuser if needed (optional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell --settings=$DJANGO_SETTINGS_MODULE << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(email='admin@innovasus.com', password='InnovaAdmin2025!', fullname='Admin User')
    print('✅ Superuser created: admin@innovasus.com/InnovaAdmin2025!')
else:
    print('ℹ️  Superuser already exists')
EOF
fi

echo "✅ Pre-deploy tasks completed!"