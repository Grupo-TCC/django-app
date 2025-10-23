# 🚀 Django to AWS MariaDB Deployment Checklist

## 📋 Pre-Deployment Checklist

### ✅ Preparation Phase

- [ ] **Backup Created**: SQLite database and media files backed up
- [ ] **AWS Account**: Active AWS account with billing configured
- [ ] **AWS CLI**: Installed and configured (`aws configure`)
- [ ] **Domain Name**: Registered (optional but recommended)
- [ ] **SSH Key**: Generated for EC2 access
- [ ] **Gmail App Password**: Created for email functionality

### ✅ Local Testing (Optional but Recommended)

- [ ] **Docker Installed**: For local MariaDB testing
- [ ] **Local MariaDB Test**: Run `./test-mariadb-local.sh`
- [ ] **Data Migration Test**: Verify SQLite to MariaDB migration works locally
- [ ] **Application Test**: Confirm all features work with MariaDB

## 🚀 Deployment Process

### Phase 1: AWS Infrastructure Setup

```bash
# Run the automated AWS setup
./setup-aws-infrastructure.sh
```

**What this creates:**

- [ ] EC2 instance (t3.micro)
- [ ] RDS MariaDB instance (db.t3.micro)
- [ ] Security groups (web server + database)
- [ ] SSH key pair
- [ ] VPC configuration

### Phase 2: Server Configuration

```bash
# SSH into your EC2 instance
ssh -i ~/.ssh/django-app-key ubuntu@<EC2_PUBLIC_IP>

# Run the deployment script
curl -fsSL https://raw.githubusercontent.com/Grupo-TCC/django-app/master/deploy-aws.sh | bash
# OR if you have the files locally:
./deploy-aws.sh
```

**What this configures:**

- [ ] System packages and dependencies
- [ ] Python virtual environment
- [ ] Django application deployment
- [ ] Database migrations
- [ ] Nginx web server
- [ ] Supervisor process management
- [ ] SSL certificate (if domain provided)

### Phase 3: Data Migration

```bash
# On your local machine, upload the data fixture
scp -i ~/.ssh/django-app-key \
  database_backups/backup_*/data_fixture.json \
  ubuntu@<EC2_PUBLIC_IP>:/var/www/django-app/

# On EC2 instance, import the data
cd /var/www/django-app
source venv/bin/activate
python manage.py loaddata data_fixture.json --settings=setup.settings_production
```

### Phase 4: Final Configuration

- [ ] **DNS Configuration**: Point domain to EC2 public IP
- [ ] **SSL Certificate**: Configure Let's Encrypt (if domain used)
- [ ] **Email Testing**: Verify email functionality works
- [ ] **Admin Access**: Create superuser and test admin panel
- [ ] **Application Testing**: Test all features thoroughly

## 🛠️ Quick Commands Reference

### Infrastructure Management

```bash
# Setup AWS infrastructure
./setup-aws-infrastructure.sh

# Check deployment variables
source .aws-deployment-vars
echo $RDS_ENDPOINT
echo $EC2_PUBLIC_IP
```

### Local Testing

```bash
# Test MariaDB locally
./test-mariadb-local.sh

# Create backup before deployment
./quick_backup.sh

# Verify backup integrity
python verify_backup.py <backup_name>
```

### Server Management

```bash
# Connect to EC2
ssh -i ~/.ssh/django-app-key ubuntu@<EC2_PUBLIC_IP>

# Check application status
sudo supervisorctl status django-app

# View logs
sudo tail -f /var/log/django/gunicorn.log
sudo tail -f /var/log/nginx/error.log

# Restart application
sudo supervisorctl restart django-app

# Update application
cd /var/www/django-app
git pull origin master
sudo supervisorctl restart django-app
```

### Database Management

```bash
# Connect to RDS
mysql -h <RDS_ENDPOINT> -u admin -p django_db

# Django database shell
python manage.py dbshell --settings=setup.settings_production

# Create database backup
mysqldump -h <RDS_ENDPOINT> -u admin -p django_db > backup_$(date +%Y%m%d).sql
```

## 🔍 Troubleshooting Guide

### Common Issues and Solutions

**502 Bad Gateway**

```bash
# Check gunicorn logs
sudo tail -f /var/log/django/gunicorn.log

# Restart application
sudo supervisorctl restart django-app
```

**Database Connection Error**

```bash
# Test RDS connectivity
mysql -h <RDS_ENDPOINT> -u admin -p

# Check security groups allow EC2 → RDS on port 3306
# Verify RDS endpoint in .env file
```

**Static Files Not Loading**

```bash
# Collect static files
python manage.py collectstatic --noinput --settings=setup.settings_production

# Check nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

**SSL Certificate Issues**

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Reconfigure certificate
sudo certbot --nginx -d your-domain.com
```

## 📊 Post-Deployment Monitoring

### Health Checks

- [ ] **Website Accessible**: Visit your domain/IP
- [ ] **Admin Panel**: Access `/admin/` successfully
- [ ] **Database**: All data migrated correctly
- [ ] **Media Files**: Images/videos display properly
- [ ] **Email**: Contact forms and notifications work
- [ ] **SSL**: HTTPS works (if configured)
- [ ] **Performance**: Page load times acceptable

### Monitoring Commands

```bash
# System resources
htop

# Disk usage
df -h

# Application logs
sudo tail -f /var/log/django/gunicorn.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Database connections
mysql -h <RDS_ENDPOINT> -u admin -p -e "SHOW PROCESSLIST;"
```

## 🔐 Security Checklist

### AWS Security

- [ ] **Security Groups**: Only necessary ports open
- [ ] **RDS Encryption**: Enabled
- [ ] **IAM Roles**: Least privilege access
- [ ] **VPC**: Proper subnet configuration

### Application Security

- [ ] **DEBUG=False**: In production settings
- [ ] **Secret Key**: Strong and unique
- [ ] **HTTPS**: SSL certificate configured
- [ ] **Database Password**: Strong password
- [ ] **Firewall**: Only necessary services exposed

## 🎯 Success Criteria

✅ **Deployment is successful when:**

- Website loads at your domain/IP address
- Admin panel accessible and functional
- All SQLite data migrated to MariaDB
- Media files (videos, images) display correctly
- Contact forms and email notifications work
- SSL certificate active (if domain configured)
- Application responds quickly and reliably

## 📞 Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **Django Deployment**: https://docs.djangoproject.com/en/5.2/howto/deployment/
- **MariaDB Documentation**: https://mariadb.com/docs/
- **Let's Encrypt**: https://letsencrypt.org/

---

## 🚀 Quick Start Summary

1. **Run**: `./setup-aws-infrastructure.sh` (creates AWS resources)
2. **SSH**: `ssh -i ~/.ssh/django-app-key ubuntu@<EC2_IP>`
3. **Deploy**: `./deploy-aws.sh` (configures server)
4. **Import**: Upload and load your data fixture
5. **Test**: Visit your application and verify everything works

Your Django application will be running on AWS with MariaDB! 🎉
