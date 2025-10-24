#!/bin/bash

# InnovaSus HTTPS Deployment Script
# Complete deployment with SSL certificates and custom domain

set -e

echo "🌟 InnovaSus HTTPS Deployment Starting..."
echo "========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN_NAME=""
EMAIL=""
GITHUB_REPO="https://github.com/Grupo-TCC/django-app.git"

# Get user inputs
echo -e "${BLUE}📝 InnovaSus Configuration${NC}"
read -p "Enter your domain name (e.g., innovasus.com): " DOMAIN_NAME
read -p "Enter your email for SSL certificate: " EMAIL
echo

if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${RED}❌ Domain name is required for HTTPS deployment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration:${NC}"
echo "   Domain: $DOMAIN_NAME"
echo "   Email: $EMAIL"
echo "   App: InnovaSus"
echo

# Update system
echo -e "${BLUE}📦 Updating system packages...${NC}"
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
echo -e "${BLUE}📦 Installing required packages...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    supervisor \
    git \
    mysql-client \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    certbot \
    python3-certbot-nginx \
    htop \
    ufw

# Configure firewall
echo -e "${BLUE}🔒 Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Create project directory
echo -e "${BLUE}📁 Setting up InnovaSus project directory...${NC}"
sudo rm -rf /var/www/innovasus
sudo mkdir -p /var/www/innovasus
sudo chown ubuntu:ubuntu /var/www/innovasus

# Clone repository
echo -e "${BLUE}📥 Cloning InnovaSus repository...${NC}"
cd /var/www/innovasus
git clone $GITHUB_REPO .

# Create virtual environment
echo -e "${BLUE}🐍 Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create environment file
echo -e "${BLUE}⚙️  Creating environment configuration...${NC}"
cat > .env << EOF
# InnovaSus Production Environment
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DOMAIN_NAME=$DOMAIN_NAME
AWS_EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Database Configuration
DB_HOST=$DB_HOST
DB_PORT=3306
DB_NAME=django_db
DB_USER=admin
DB_PASSWORD=$DB_PASSWORD

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF

# Create logs directory
mkdir -p logs

# Run Django setup
echo -e "${BLUE}🗄️  Setting up Django database...${NC}"
python manage.py migrate --settings=setup.settings_production
python manage.py collectstatic --noinput --settings=setup.settings_production

# Create superuser
echo -e "${BLUE}👤 Creating InnovaSus admin user...${NC}"
echo -e "${YELLOW}Please create admin password:${NC}"
read -s -p "Enter admin password: " ADMIN_PASSWORD
echo
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@innovasus.com', '$ADMIN_PASSWORD', fullname='InnovaSus Admin') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell --settings=setup.settings_production

# Configure Supervisor
echo -e "${BLUE}🔧 Configuring Supervisor for InnovaSus...${NC}"
sudo tee /etc/supervisor/conf.d/innovasus.conf > /dev/null << EOF
[program:innovasus]
command=/var/www/innovasus/venv/bin/gunicorn setup.wsgi:application --bind 127.0.0.1:8000 --workers 3
directory=/var/www/innovasus
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/innovasus.log
environment=DJANGO_SETTINGS_MODULE=setup.settings_production
EOF

# Configure Nginx (HTTP first, then add SSL)
echo -e "${BLUE}🌐 Configuring Nginx for InnovaSus...${NC}"
sudo tee /etc/nginx/sites-available/innovasus > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/innovasus;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /var/www/innovasus;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable site
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/innovasus /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Start services
echo -e "${BLUE}🚀 Starting InnovaSus services...${NC}"
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start innovasus
sudo systemctl restart nginx

# Get SSL certificate
echo -e "${BLUE}🔒 Getting SSL certificate for InnovaSus...${NC}"
sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL --redirect

# Final status check
echo -e "${GREEN}🎉 InnovaSus deployment completed!${NC}"
echo "========================================="
echo -e "${GREEN}✅ InnovaSus is now live at:${NC}"
echo -e "${BLUE}   https://$DOMAIN_NAME${NC}"
echo -e "${BLUE}   https://www.$DOMAIN_NAME${NC}"
echo
echo -e "${GREEN}🔑 Admin Access:${NC}"
echo -e "${BLUE}   URL: https://$DOMAIN_NAME/admin/${NC}"
echo -e "${BLUE}   Username: admin${NC}"
echo -e "${BLUE}   Password: [Your chosen password]${NC}"
echo
echo -e "${GREEN}📊 Service Status:${NC}"
sudo supervisorctl status innovasus
sudo systemctl status nginx --no-pager -l | head -5

echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo "1. Point your domain DNS to this server's IP"
echo "2. Update admin password in Django admin"
echo "3. Configure email settings"
echo "4. Set up regular backups"