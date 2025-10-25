import os
import sys

# Add your project directory to Python path
# Replace 'u123456789' with your actual Hostinger username
project_home = '/home/u123456789/domains/innovasusbr.com/public_html'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set Django settings module for shared hosting
os.environ['DJANGO_SETTINGS_MODULE'] = 'setup.settings_hostinger'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()