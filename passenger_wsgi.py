"""
WSGI config for InnovaSUS project on Hostinger VPS.
This file is used by Gunicorn for VPS deployment.
"""

import os
import sys
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set the settings module for VPS production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings_hostinger')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()