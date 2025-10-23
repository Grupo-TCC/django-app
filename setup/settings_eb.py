"""
Elastic Beanstalk settings for InnovaSus
"""
import os
from .settings import *

# SECURITY SETTINGS
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# AWS EB provides the hostname
ALLOWED_HOSTS = ['*']  # EB handles this securely

# Use SQLite for now (can be upgraded to RDS later)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# HTTPS Settings (EB handles SSL termination)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
