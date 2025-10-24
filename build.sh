#!/bin/bash

# InnovaSus Build Script for Render.com
echo "🚀 Building InnovaSus for Render deployment..."

# Install optimized requirements for faster builds
echo "📦 Installing dependencies..."
pip install -r requirements-render.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=setup.settings_render

echo "✅ InnovaSus build complete!"
