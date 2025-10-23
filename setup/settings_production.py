"""
Production settings for AWS deployment with MariaDB
"""
import os
import environ
from .settings import *

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False)
)

# SECURITY SETTINGS
DEBUG = env('DEBUG', default=False)
SECRET_KEY = env('SECRET_KEY')

# ALLOWED HOSTS for production
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    env('DOMAIN_NAME', default=''),  # Your domain
    env('AWS_EC2_PUBLIC_IP', default=''),  # EC2 public IP
    '.elasticbeanstalk.com',  # If using Elastic Beanstalk
    '.amazonaws.com',
]

# DATABASE CONFIGURATION for MariaDB on AWS RDS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME', default='django_db'),
        'USER': env('DB_USER', default='admin'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),  # RDS endpoint
        'PORT': env('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# STATIC FILES CONFIGURATION for AWS S3 (optional)
USE_S3 = env('USE_S3', default=False)

if USE_S3:
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.MediaS3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Local static files with WhiteNoise
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# SECURITY SETTINGS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    # Temporarily disable HTTPS redirect for HTTP access
    # SECURE_SSL_REDIRECT = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# CSRF TRUSTED ORIGINS
CSRF_TRUSTED_ORIGINS = [
    f"https://{env('DOMAIN_NAME', default='')}",
    f"http://{env('AWS_EC2_PUBLIC_IP', default='')}",
    f"https://{env('AWS_EC2_PUBLIC_IP', default='')}",
]

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# EMAIL CONFIGURATION (using AWS SES optionally)
if env('USE_AWS_SES', default=False):
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_REGION_NAME = env('AWS_SES_REGION_NAME', default='us-east-1')
    AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'
else:
    # Gmail SMTP Configuration (fallback)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='innovasus76@gmail.com')
    EMAIL_HOST_PASSWORD = env('GMAIL_APP_PASSWORD')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    EMAIL_TIMEOUT = 30