#!/bin/bash

# InnovaSus Static Files Collection
echo "📁 Collecting static files for InnovaSus..."
python manage.py collectstatic --noinput --settings=setup.settings_render
echo "✅ Static files ready!"
