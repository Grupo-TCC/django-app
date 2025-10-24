"""
Build-time settings for Docker builds
No environment variables required
"""
from .settings import *

# Build-time settings
DEBUG = False
SECRET_KEY = 'build-time-key-not-used-in-production'

# Allow all hosts during build
ALLOWED_HOSTS = ['*']

# Use in-memory database for collectstatic
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Minimal configuration for building
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

print("🔨 InnovaSus Build Settings Loaded - No Environment Variables Required")