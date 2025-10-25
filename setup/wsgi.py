"""
WSGI config for InnovaSUS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For VPS deployment, this uses settings_hostinger for production configuration.
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings for VPS deployment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings_hostinger')

application = get_wsgi_application()
