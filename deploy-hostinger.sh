#!/bin/bash

# InnovaSus Hostinger Deployment Script
# Run this script on your Hostinger VPS

set -e

echo "🚀 Starting InnovaSus deployment on Hostinger..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install python3 python3-pip python3-venv nginx mysql-server git supervisor ufw -y

# Create application directory
print_status "Setting up application directory..."
mkdir -p /var/www/innovasus
cd /var/www/innovasus

# Clone repository
print_status "Cloning InnovaSus repository..."
if [ -d ".git" ]; then
    git pull
else
    git clone https://github.com/Grupo-TCC/django-app.git .
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-hostinger.txt

# Prompt for configuration
print_warning "Please provide the following information:"

read -p "Enter your domain name [innovasusbr.com]: " DOMAIN_NAME
DOMAIN_NAME=${DOMAIN_NAME:-innovasusbr.com}
read -p "Enter your server IP: " SERVER_IP
read -s -p "Enter MySQL root password: " MYSQL_ROOT_PASSWORD
echo
read -p "Enter database name [innovasus_db]: " DB_NAME
DB_NAME=${DB_NAME:-innovasus_db}
read -p "Enter database user [innovasus_user]: " DB_USER
DB_USER=${DB_USER:-innovasus_user}
read -s -p "Enter database password: " DB_PASSWORD
echo
read -s -p "Enter Django secret key: " SECRET_KEY
echo
read -p "Enter Gmail address [innovasus76@gmail.com]: " EMAIL_HOST_USER
EMAIL_HOST_USER=${EMAIL_HOST_USER:-innovasus76@gmail.com}
read -s -p "Enter Gmail app password: " GMAIL_APP_PASSWORD
echo

# Setup MySQL database
print_status "Setting up MySQL database..."
mysql -u root -p${MYSQL_ROOT_PASSWORD} << EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

# Create environment file
print_status "Creating environment configuration..."
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=${SECRET_KEY}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=${EMAIL_HOST_USER}
GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD}
DJANGO_SETTINGS_MODULE=setup.settings_hostinger
CREATE_SUPERUSER=true
EOF

# Update ALLOWED_HOSTS in settings
print_status "Updating Django settings..."
sed -i "s/your-domain.com/${DOMAIN_NAME}/g" setup/settings_hostinger.py
sed -i "s/your-server-ip/${SERVER_IP}/g" setup/settings_hostinger.py

# Run Django setup
print_status "Running Django migrations and setup..."
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=setup.settings_hostinger
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py create_admin

# Create Gunicorn service
print_status "Setting up Gunicorn service..."
cat > /etc/systemd/system/innovasus.service << EOF
[Unit]
Description=InnovaSus Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/innovasus
Environment="PATH=/var/www/innovasus/venv/bin"
EnvironmentFile=/var/www/innovasus/.env.production
ExecStart=/var/www/innovasus/venv/bin/gunicorn --workers 3 --bind unix:/var/www/innovasus/innovasus.sock setup.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start Gunicorn service
systemctl daemon-reload
systemctl start innovasus
systemctl enable innovasus

# Create Nginx configuration
print_status "Setting up Nginx..."
cat > /etc/nginx/sites-available/innovasus << EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME} ${SERVER_IP};
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/innovasus;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /var/www/innovasus;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/innovasus/innovasus.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/innovasus /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

# Set permissions
print_status "Setting file permissions..."
chown -R www-data:www-data /var/www/innovasus
chmod -R 755 /var/www/innovasus

# Configure firewall
print_status "Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Install SSL certificate
print_status "Installing SSL certificate..."
apt install certbot python3-certbot-nginx -y

print_status "Attempting to get SSL certificate..."
if certbot --nginx -d ${DOMAIN_NAME} -d www.${DOMAIN_NAME} --non-interactive --agree-tos --email ${EMAIL_HOST_USER}; then
    print_status "SSL certificate installed successfully!"
else
    print_warning "SSL certificate installation failed. You can run this manually later:"
    echo "certbot --nginx -d ${DOMAIN_NAME} -d www.${DOMAIN_NAME}"
fi

# Final status check
print_status "Checking service status..."
systemctl status innovasus --no-pager
systemctl status nginx --no-pager

print_status "🎉 Deployment completed successfully!"
print_status "Your Django app should be available at:"
echo "  - HTTP: http://${DOMAIN_NAME}"
echo "  - HTTPS: https://${DOMAIN_NAME} (if SSL was successful)"
echo "  - Admin: https://${DOMAIN_NAME}/admin/"
echo ""
print_status "Admin credentials:"
echo "  - Email: admin@innovasus.com"
echo "  - Password: InnovaAdmin2025!"
echo ""
print_status "To check logs:"
echo "  - Django: journalctl -u innovasus -f"
echo "  - Nginx: tail -f /var/log/nginx/error.log"