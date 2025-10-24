"""
Production settings for Render.com deployment with PostgreSQL
Optimized for Render platform
"""
import os
from urllib.parse import urlparse
from .settings import *

# SECURITY SETTINGS
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'render-production-key-change-this')

# ALLOWED HOSTS for Render
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Render domains
    os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''),
]

# Remove empty hosts
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# Add wildcard for Render if no specific domain
if not any('.onrender.com' in host for host in ALLOWED_HOSTS):
    ALLOWED_HOSTS.append('*')

# DATABASE CONFIGURATION for Render PostgreSQL
if 'DATABASE_URL' in os.environ:
    # Parse DATABASE_URL manually for Render PostgreSQL
    url = urlparse(os.environ.get('DATABASE_URL'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],  # Remove leading slash
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
            'OPTIONS': {
                'connect_timeout': 60,
            },
        }
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

# HTTPS and Security (Render provides HTTPS automatically)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Render handles this
USE_TLS = True

# Email Configuration (using your Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 60
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'innovasus76@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Email debugging
EMAIL_DEBUG = True

# Logging for Render
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

# Render-specific settings
if 'RENDER' in os.environ:
    # Running on Render
    SECURE_SSL_REDIRECT = False  # Render handles SSL termination
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    
print("🌟 InnovaSus Production Settings Loaded for Render.com!")