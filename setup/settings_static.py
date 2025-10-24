"""
InnovaSus Static Hosting Settings
For deployment to free platforms while AWS account verifies
"""
from .settings import *
import os

# Free hosting domains
ALLOWED_HOSTS = [
    'innovasus.vercel.app',
    'innovasus.netlify.app', 
    'grupo-tcc.github.io',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    '*',  # Allow all for now
]

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Collect all static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security for free hosting
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'innovasus-static-2025')

# Database for static demos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

print("🌟 InnovaSus Static Hosting Settings Loaded - Free Deployment Ready!")
