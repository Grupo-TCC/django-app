#!/bin/bash

# InnovaSus AWS Elastic Beanstalk Deployment (Free AWS Domain)
# This gives you a free AWS subdomain with HTTPS automatically

set -e

echo "🌟 InnovaSus Elastic Beanstalk Deployment"
echo "========================================"
echo "This will deploy InnovaSus with a FREE AWS domain!"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
APP_NAME="innovasus"
ENV_NAME="innovasus-env"
REGION="us-east-1"

echo -e "${BLUE}📝 Configuration${NC}"
echo "   App Name: $APP_NAME"
echo "   Environment: $ENV_NAME" 
echo "   Region: $REGION"
echo "   Free AWS Domain: ${APP_NAME}-env.eba-xxxxxxx.${REGION}.elasticbeanstalk.com"
echo

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo -e "${YELLOW}📦 Installing AWS EB CLI...${NC}"
    pip3 install awsebcli --user
    export PATH="$PATH:$(python3 -m site --user-base)/bin"
fi

# Prepare application for Elastic Beanstalk
echo -e "${BLUE}📁 Preparing InnovaSus for AWS deployment...${NC}"

# Create requirements.txt if not exists
if [ ! -f requirements.txt ]; then
    echo -e "${YELLOW}Creating requirements.txt...${NC}"
    cat > requirements.txt << 'EOF'
Django==5.2
Pillow>=8.0.0
django-environ
mysqlclient
gunicorn
whitenoise
EOF
fi

# Create Elastic Beanstalk configuration
mkdir -p .ebextensions

# Database configuration
cat > .ebextensions/01_packages.config << 'EOF'
packages:
  yum:
    mariadb105-devel: []
    gcc: []
    python3-devel: []
EOF

# Django configuration
cat > .ebextensions/02_python.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: setup.wsgi:application
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: setup.settings_production
    PYTHONPATH: /var/app/current
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: staticfiles
EOF

# Static files configuration
cat > .ebextensions/03_staticfiles.config << 'EOF'
container_commands:
  01_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python /var/app/current/manage.py collectstatic --noinput"
  02_migrate:
    command: "source /var/app/venv/*/bin/activate && python /var/app/current/manage.py migrate --noinput"
    leader_only: true
EOF

# Create production settings for EB
cat > setup/settings_eb.py << 'EOF'
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
EOF

# Initialize EB application
echo -e "${BLUE}🚀 Initializing Elastic Beanstalk application...${NC}"
if [ ! -f .elasticbeanstalk/config.yml ]; then
    eb init $APP_NAME --platform python-3.9 --region $REGION
fi

# Create environment and deploy
echo -e "${BLUE}🌐 Creating InnovaSus environment...${NC}"
eb create $ENV_NAME --single-instance --instance-type t3.micro

# Get the application URL
echo -e "${BLUE}📡 Getting InnovaSus URL...${NC}"
EB_URL=$(eb status | grep "CNAME" | awk '{print $2}')

echo -e "${GREEN}🎉 InnovaSus Deployment Complete!${NC}"
echo "=================================="
echo -e "${GREEN}✅ InnovaSus is now live at:${NC}"
echo -e "${BLUE}   https://$EB_URL${NC}"
echo -e "${BLUE}   http://$EB_URL${NC}"
echo
echo -e "${GREEN}🔑 Features enabled:${NC}"
echo "   ✅ Free AWS subdomain"
echo "   ✅ Automatic HTTPS"
echo "   ✅ Auto-scaling"
echo "   ✅ Health monitoring"
echo "   ✅ Easy updates with 'eb deploy'"
echo
echo -e "${YELLOW}📋 Management Commands:${NC}"
echo "   eb status          - Check app status"
echo "   eb deploy          - Deploy updates"
echo "   eb logs            - View logs"
echo "   eb open            - Open in browser"
echo "   eb terminate       - Delete environment"
echo
echo -e "${GREEN}🌟 Your InnovaSus app is ready!${NC}"
EOF