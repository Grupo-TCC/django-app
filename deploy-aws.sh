#!/bin/bash

# AWS EC2 Deployment Script for Django + MariaDB
# Run this script on your EC2 instance after infrastructure setup

set -e

echo "🚀 Starting Django deployment on AWS EC2..."

# Check if running on EC2
if ! curl -s --max-time 5 http://169.254.169.254/latest/meta-data/instance-id &>/dev/null; then
    echo "⚠️  This script should be run on an EC2 instance"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get user inputs
read -p "Enter your GitHub repository URL: " REPO_URL
read -p "Enter RDS endpoint: " RDS_ENDPOINT
read -p "Enter database password: " -s DB_PASSWORD
echo
read -p "Enter your domain name (or press enter for IP-only): " DOMAIN_NAME
read -p "Enter Gmail app password (for email): " -s GMAIL_PASSWORD
echo

# Update system
echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
echo "📦 Installing required packages..."
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
    htop

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/django-app
sudo chown ubuntu:ubuntu /var/www/django-app

# Clone repository
echo "📥 Cloning repository..."
cd /var/www/django-app
git clone $REPO_URL .

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Get EC2 metadata
EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "unknown")
EC2_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id || echo "unknown")

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Django Settings
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DOMAIN_NAME=$DOMAIN_NAME
AWS_EC2_PUBLIC_IP=$EC2_PUBLIC_IP

# MariaDB Database
DB_NAME=django_db
DB_USER=admin
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$RDS_ENDPOINT
DB_PORT=3306

# AWS Instance Info
EC2_INSTANCE_ID=$EC2_INSTANCE_ID

# Email Configuration
GMAIL_APP_PASSWORD=$GMAIL_PASSWORD

# Optional: AWS S3 (disabled by default)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
EOF

echo "✅ Environment file created"

# Test database connection
echo "🔌 Testing database connection..."
if mysql -h $RDS_ENDPOINT -u admin -p$DB_PASSWORD -e "SELECT 1;" &>/dev/null; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed. Please check your RDS endpoint and password."
    exit 1
fi

# Run Django setup
echo "🔄 Running Django migrations..."
python manage.py migrate --settings=setup.settings_production

# Create superuser
echo "👤 Creating Django superuser..."
echo "Please create a superuser account:"
python manage.py createsuperuser --settings=setup.settings_production

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=setup.settings_production

# Create necessary directories
echo "📁 Creating necessary directories..."
sudo mkdir -p /var/log/django
sudo chown ubuntu:ubuntu /var/log/django

# Set permissions
sudo chown -R ubuntu:ubuntu /var/www/django-app
sudo chmod -R 755 /var/www/django-app

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/django-app

# Update nginx config with actual values
sudo sed -i "s/your-domain.com/$DOMAIN_NAME/g" /etc/nginx/sites-available/django-app
sudo sed -i "s/your-ec2-public-ip/$EC2_PUBLIC_IP/g" /etc/nginx/sites-available/django-app

# Enable the site
sudo ln -sf /etc/nginx/sites-available/django-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
if sudo nginx -t; then
    echo "✅ Nginx configuration valid"
    sudo systemctl restart nginx
    sudo systemctl enable nginx
else
    echo "❌ Nginx configuration error"
    exit 1
fi

# Configure Supervisor
echo "⚙️ Configuring Supervisor..."
sudo cp supervisor.conf /etc/supervisor/conf.d/django-app.conf

# Update supervisor and start the application
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start django-app

# Check application status
echo "📊 Checking application status..."
sleep 3
if sudo supervisorctl status django-app | grep RUNNING; then
    echo "✅ Django application is running"
else
    echo "❌ Django application failed to start"
    echo "Check logs: sudo tail -f /var/log/django/gunicorn.log"
    exit 1
fi

# Setup SSL certificate (if domain provided)
if [ ! -z "$DOMAIN_NAME" ] && [ "$DOMAIN_NAME" != "" ]; then
    echo "🔒 Setting up SSL certificate..."
    echo "Note: Make sure your domain DNS points to $EC2_PUBLIC_IP before proceeding"
    read -p "Has your domain DNS been configured? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME
        echo "✅ SSL certificate installed"
    else
        echo "⚠️  SSL setup skipped. Run this command later:"
        echo "sudo certbot --nginx -d $DOMAIN_NAME"
    fi
fi

# Create deployment summary
cat > ~/deployment-summary.txt << EOF
🎉 Django Deployment Complete!
=============================

Application URL:
$(if [ ! -z "$DOMAIN_NAME" ]; then echo "- https://$DOMAIN_NAME"; fi)
- http://$EC2_PUBLIC_IP
- https://$EC2_PUBLIC_IP (if SSL configured)

Admin Panel:
$(if [ ! -z "$DOMAIN_NAME" ]; then echo "- https://$DOMAIN_NAME/admin/"; fi)
- http://$EC2_PUBLIC_IP/admin/

Database:
- Host: $RDS_ENDPOINT
- Database: django_db
- User: admin

Useful Commands:
- Restart app: sudo supervisorctl restart django-app
- Check logs: sudo tail -f /var/log/django/gunicorn.log
- Nginx logs: sudo tail -f /var/log/nginx/error.log
- Update code: cd /var/www/django-app && git pull && sudo supervisorctl restart django-app

Security:
- Firewall: Configured via AWS Security Groups
- SSL: $(if [ ! -z "$DOMAIN_NAME" ]; then echo "Configured"; else echo "Not configured (IP access only)"; fi)
- Database: Private subnet, encrypted storage

Next Steps:
1. Import your data from SQLite backup
2. Test all functionality
3. Configure monitoring and backups
4. Set up CI/CD pipeline (optional)

Deployment completed at: $(date)
EOF

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "🌐 Your application is now running at:"
if [ ! -z "$DOMAIN_NAME" ]; then
    echo "   https://$DOMAIN_NAME"
fi
echo "   http://$EC2_PUBLIC_IP"
echo ""
echo "🔧 Admin panel:"
echo "   http://$EC2_PUBLIC_IP/admin/"
echo ""
echo "📋 Summary saved to: ~/deployment-summary.txt"
echo ""
echo "📊 Check application status:"
echo "   sudo supervisorctl status"
echo ""
echo "📝 View logs:"
echo "   sudo tail -f /var/log/django/gunicorn.log"
echo ""
echo "🔄 To import your SQLite data:"
echo "   1. Upload your data_fixture.json file"
echo "   2. Run: python manage.py loaddata data_fixture.json --settings=setup.settings_production"
echo ""
echo "🆘 If you encounter issues:"
echo "   - Check logs above"
echo "   - Verify RDS is accessible"
echo "   - Ensure security groups are configured correctly"