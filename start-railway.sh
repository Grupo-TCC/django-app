#!/bin/bash

# InnovaSus Railway Startup Script
echo "🚀 Starting InnovaSus on Railway..."

# Install Railway-optimized requirements (faster than main requirements.txt)
echo "📦 Installing Railway-optimized dependencies..."
pip install -r requirements-railway.txt

# Set default environment variables if not provided
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"setup.settings_railway"}
export SECRET_KEY=${SECRET_KEY:-"railway-default-key-change-this"}
export DEBUG=${DEBUG:-"False"}

# Run migrations
echo "📊 Running database migrations..."
python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=$DJANGO_SETTINGS_MODULE

# Create superuser if needed (optional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell --settings=$DJANGO_SETTINGS_MODULE << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@innovasus.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF
fi

# Start Gunicorn
echo "🌟 Starting InnovaSus server..."
exec gunicorn setup.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info