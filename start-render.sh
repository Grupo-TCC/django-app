#!/bin/bash

# InnovaSus Render.com Pre-Deploy Script
# This runs before the server starts
echo "🌟 InnovaSus Pre-Deploy Tasks..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"setup.settings_render"}

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE

# Create superuser using management command
echo "👤 Creating superuser..."
python manage.py create_admin --settings=$DJANGO_SETTINGS_MODULE

echo "✅ Pre-deploy tasks completed!"