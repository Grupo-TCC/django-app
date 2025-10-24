"""
Production settings for Railway deployment with PostgreSQL
"""
import os
import dj_database_url
from .settings import *

# SECURITY SETTINGS
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'railway-production-key-change-this')

# ALLOWED HOSTS for Railway
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',  # Railway domains
    '.up.railway.app',  # Alternative Railway domains
    os.environ.get('RAILWAY_STATIC_URL', '').replace('https://', '').replace('http://', ''),
]

# Remove empty hosts
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# Add wildcard for Railway if no specific domain
if not any('.railway.app' in host for host in ALLOWED_HOSTS):
    ALLOWED_HOSTS.append('*')

# DATABASE CONFIGURATION for Railway PostgreSQL
if 'DATABASE_URL' in os.environ:
    # Railway provides DATABASE_URL automatically
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Fallback to SQLite for local testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# STATIC FILES CONFIGURATION
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES CONFIGURATION
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# HTTPS and Security (Railway provides HTTPS automatically)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Railway handles this
USE_TLS = True

# Email Configuration (using your Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'innovasus76@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Logging for Railway
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
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Railway-specific settings
if 'RAILWAY_ENVIRONMENT' in os.environ:
    # Running on Railway
    SECURE_SSL_REDIRECT = False  # Railway handles SSL termination
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    
print("🚀 InnovaSus Production Settings Loaded for Railway!")