"""
Static site settings for AWS Amplify deployment
"""
from .settings import *
import os

# Static files configuration
STATIC_URL = '/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Collect all static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Basic settings for static build
DEBUG = False
SECRET_KEY = 'static-build-key'
ALLOWED_HOSTS = ['*']

# Minimal database for collectstatic
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
