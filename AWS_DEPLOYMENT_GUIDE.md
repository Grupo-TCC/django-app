# 🚀 AWS Deployment Guide: Django + MariaDB

## 📋 Overview

This guide will help you deploy your Django application to AWS using:

- **EC2** for hosting the Django application
- **RDS MariaDB** for the database
- **S3** (optional) for static/media files
- **Route 53** (optional) for custom domain

## 🏗️ Architecture Overview

```
Internet → Route 53 → EC2 (Django + Nginx) → RDS (MariaDB)
                    ↓
                   S3 (Static/Media Files)
```

## 📋 Prerequisites

- AWS Account with billing enabled
- AWS CLI installed locally
- SSH key pair for EC2
- Domain name (optional)

## 🎯 Phase 1: AWS Setup

### Step 1.1: Install AWS CLI (if not installed)

```bash
# macOS
brew install awscli

# Or download from: https://aws.amazon.com/cli/
```

### Step 1.2: Configure AWS CLI

```bash
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Output format (json)
```

### Step 1.3: Create SSH Key Pair

```bash
# Generate new key pair (if you don't have one)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/django-app-key

# Upload to AWS
aws ec2 import-key-pair \
  --key-name django-app-key \
  --public-key-material fileb://~/.ssh/django-app-key.pub
```

## 🎯 Phase 2: Setup RDS MariaDB

### Step 2.1: Create RDS Subnet Group

```bash
# Create subnet group for RDS
aws rds create-db-subnet-group \
  --db-subnet-group-name django-db-subnet-group \
  --db-subnet-group-description "Subnet group for Django MariaDB" \
  --subnet-ids subnet-12345678 subnet-87654321 \
  --tags Key=Name,Value=django-db-subnet-group
```

### Step 2.2: Create Security Group for RDS

```bash
# Create security group for database
aws ec2 create-security-group \
  --group-name django-db-sg \
  --description "Security group for Django MariaDB database"

# Allow MySQL/MariaDB access from EC2 instances
aws ec2 authorize-security-group-ingress \
  --group-name django-db-sg \
  --protocol tcp \
  --port 3306 \
  --source-group django-web-sg
```

### Step 2.3: Create RDS MariaDB Instance

```bash
# Create MariaDB instance
aws rds create-db-instance \
  --db-instance-identifier django-mariadb \
  --db-instance-class db.t3.micro \
  --engine mariadb \
  --engine-version 10.11.8 \
  --master-username admin \
  --master-user-password 'YourStrongPassword123!' \
  --allocated-storage 20 \
  --storage-type gp2 \
  --db-name django_db \
  --vpc-security-group-ids sg-12345678 \
  --db-subnet-group-name django-db-subnet-group \
  --backup-retention-period 7 \
  --storage-encrypted \
  --tags Key=Name,Value=django-mariadb
```

## 🎯 Phase 3: Setup EC2 Instance

### Step 3.1: Create Security Group for Web Server

```bash
# Create security group for web server
aws ec2 create-security-group \
  --group-name django-web-sg \
  --description "Security group for Django web server"

# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
  --group-name django-web-sg \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS traffic
aws ec2 authorize-security-group-ingress \
  --group-name django-web-sg \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow SSH access
aws ec2 authorize-security-group-ingress \
  --group-name django-web-sg \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

### Step 3.2: Launch EC2 Instance

```bash
# Launch Ubuntu EC2 instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.micro \
  --key-name django-app-key \
  --security-groups django-web-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=django-web-server}]'
```

## 🎯 Phase 4: Configure EC2 Instance

### Step 4.1: Connect to EC2

```bash
# Get EC2 public IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=django-web-server" \
  --query "Reservations[*].Instances[*].[PublicIpAddress]" \
  --output text

# Connect via SSH
ssh -i ~/.ssh/django-app-key ubuntu@<EC2_PUBLIC_IP>
```

### Step 4.2: Setup Server Environment

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
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
  certbot \
  python3-certbot-nginx

# Create application directory
sudo mkdir -p /var/www/django-app
sudo chown ubuntu:ubuntu /var/www/django-app
```

### Step 4.3: Deploy Application

```bash
# Clone your repository
cd /var/www/django-app
git clone https://github.com/Grupo-TCC/django-app.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4.4: Configure Environment Variables

```bash
# Create production environment file
cat > .env << EOF
# Django Settings
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DOMAIN_NAME=your-domain.com
AWS_EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# MariaDB Database (Replace with your RDS endpoint)
DB_NAME=django_db
DB_USER=admin
DB_PASSWORD=YourStrongPassword123!
DB_HOST=django-mariadb.cluster-xxxxx.us-east-1.rds.amazonaws.com
DB_PORT=3306

# Optional: AWS S3 for static files
USE_S3=False
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Email
GMAIL_APP_PASSWORD=your-gmail-app-password
EOF
```

## 🎯 Phase 5: Database Migration

### Step 5.1: Test Database Connection

```bash
# Test MariaDB connection
mysql -h django-mariadb.cluster-xxxxx.us-east-1.rds.amazonaws.com \
      -u admin -p django_db

# If successful, exit MySQL and continue
```

### Step 5.2: Run Django Migrations

```bash
# Run migrations on production database
source venv/bin/activate
python manage.py migrate --settings=setup.settings_production

# Create superuser
python manage.py createsuperuser --settings=setup.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=setup.settings_production
```

### Step 5.3: Import Data from SQLite

```bash
# Copy your data fixture to the server (from your local machine)
scp -i ~/.ssh/django-app-key \
  database_backups/backup_*/data_fixture.json \
  ubuntu@<EC2_PUBLIC_IP>:/var/www/django-app/

# On the server, import data
python manage.py loaddata data_fixture.json --settings=setup.settings_production
```

## 🎯 Phase 6: Configure Web Server

### Step 6.1: Setup Nginx

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/django-app

# Edit the configuration with your domain/IP
sudo nano /etc/nginx/sites-available/django-app
# Replace 'your-domain.com your-ec2-public-ip' with actual values

# Enable the site
sudo ln -s /etc/nginx/sites-available/django-app /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 6.2: Setup Supervisor

```bash
# Copy supervisor configuration
sudo cp supervisor.conf /etc/supervisor/conf.d/django-app.conf

# Create log directory
sudo mkdir -p /var/log/django
sudo chown ubuntu:ubuntu /var/log/django

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start django-app

# Check status
sudo supervisorctl status
```

## 🎯 Phase 7: SSL Certificate (Optional)

### Step 7.1: Setup SSL with Let's Encrypt

```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

## 🎯 Phase 8: S3 for Static Files (Optional)

### Step 8.1: Create S3 Bucket

```bash
# Create S3 bucket
aws s3 mb s3://your-django-app-static-files

# Configure bucket policy for public read access
aws s3api put-bucket-policy \
  --bucket your-django-app-static-files \
  --policy file://s3-bucket-policy.json
```

### Step 8.2: Update Environment Variables

```bash
# Update .env file
USE_S3=True
AWS_STORAGE_BUCKET_NAME=your-django-app-static-files

# Restart application
sudo supervisorctl restart django-app
```

## 🎯 Phase 9: Testing & Monitoring

### Step 9.1: Test Your Application

```bash
# Check application status
curl -I http://your-domain.com
curl -I https://your-domain.com

# Check database connection
python manage.py check --settings=setup.settings_production

# Check logs
sudo tail -f /var/log/django/gunicorn.log
sudo tail -f /var/log/nginx/access.log
```

### Step 9.2: Setup Monitoring

```bash
# Install htop for system monitoring
sudo apt-get install htop

# Setup log rotation
sudo nano /etc/logrotate.d/django-app
```

## 🛠️ Maintenance Commands

### Application Management

```bash
# Restart application
sudo supervisorctl restart django-app

# Update application
cd /var/www/django-app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=setup.settings_production
python manage.py collectstatic --noinput --settings=setup.settings_production
sudo supervisorctl restart django-app
```

### Database Backup

```bash
# Create database backup
mysqldump -h django-mariadb.cluster-xxxxx.us-east-1.rds.amazonaws.com \
  -u admin -p django_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 🚨 Troubleshooting

### Common Issues

1. **502 Bad Gateway** - Check gunicorn logs: `sudo tail -f /var/log/django/gunicorn.log`
2. **Database Connection** - Verify RDS security group allows EC2 access
3. **Static Files** - Run `collectstatic` and check nginx configuration
4. **SSL Issues** - Check certbot logs: `sudo tail -f /var/log/letsencrypt/letsencrypt.log`

### Security Checklist

- [ ] RDS encryption enabled
- [ ] Security groups properly configured
- [ ] SSL certificate installed
- [ ] Django DEBUG=False
- [ ] Strong database passwords
- [ ] Regular backups scheduled

## 📞 Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **Django Deployment**: https://docs.djangoproject.com/en/5.2/howto/deployment/
- **Let's Encrypt**: https://letsencrypt.org/getting-started/

Your Django application should now be running on AWS with MariaDB! 🎉
