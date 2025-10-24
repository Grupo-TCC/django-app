#!/bin/bash

# InnovaSus Render.com Startup Script
echo "🌟 Starting InnovaSus on Render..."

# Set default environment variables
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"setup.settings_railway"}
export SECRET_KEY=${SECRET_KEY:-"render-default-key"}
export DEBUG=${DEBUG:-"False"}

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
    User.objects.create_superuser('admin', 'admin@innovasus.com', 'InnovaAdmin2025!')
    print('✅ Superuser created: admin/InnovaAdmin2025!')
else:
    print('ℹ️  Superuser already exists')
EOF
fi

# Start Gunicorn with optimized settings for Render
echo "🚀 Starting InnovaSus server on Render..."
exec gunicorn setup.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info