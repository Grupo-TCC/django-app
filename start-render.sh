#!/bin/bash

# InnovaSus Render.com Release Script
# This runs during build, not during server start
echo "🌟 InnovaSus Release Tasks..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"setup.settings_render"}

# Check if Django is installed
echo "🔍 Checking Django installation..."
python -c "import django; print(f'✅ Django {django.VERSION} found')" || {
    echo "❌ Django not found! Installing dependencies..."
    pip install -r requirements-render.txt
}

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

echo "✅ Release tasks completed!"