#!/bin/bash

# InnovaSus Build Script for Render.com
echo "🚀 Building InnovaSus for Render deployment..."

# Install optimized requirements for faster builds
echo "📦 Installing dependencies..."
pip install -r requirements-railway.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=setup.settings_railway

echo "✅ InnovaSus build complete!"
