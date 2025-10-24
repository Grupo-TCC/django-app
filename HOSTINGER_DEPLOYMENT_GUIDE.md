# InnovaSus - Hostinger Deployment Guide

## 🚀 Hostinger VPS Django Deployment

### Prerequisites

1. **Hostinger VPS** with Ubuntu/CentOS
2. **Domain** pointed to your VPS
3. **SSH access** to your server

## 📋 Step-by-Step Deployment

### 1. Server Setup

#### Connect to your VPS:

```bash
ssh root@your-server-ip
```

#### Update system:

```bash
apt update && apt upgrade -y
```

#### Install required packages:

```bash
apt install python3 python3-pip python3-venv nginx mysql-server git supervisor -y
```

### 2. MySQL Database Setup

#### Secure MySQL installation:

```bash
mysql_secure_installation
```

#### Create database and user:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE innovasus_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'innovasus_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON innovasus_db.* TO 'innovasus_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Deploy Django Application

#### Create application directory:

```bash
mkdir -p /var/www/innovasus
cd /var/www/innovasus
```

#### Clone your repository:

```bash
git clone https://github.com/Grupo-TCC/django-app.git .
```

#### Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies:

```bash
pip install -r requirements-hostinger.txt
```

#### Create environment file:

```bash
nano .env.production
```

Add this content:

```bash
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
DB_NAME=innovasus_db
DB_USER=innovasus_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=innovasus76@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
DJANGO_SETTINGS_MODULE=setup.settings_hostinger
```

#### Update ALLOWED_HOSTS:

Edit `setup/settings_hostinger.py` and replace:

```python
ALLOWED_HOSTS = [
    'your-actual-domain.com',
    'www.your-actual-domain.com',
    'your-server-ip',
]
```

#### Run migrations and collect static files:

```bash
source venv/bin/activate
python manage.py migrate --settings=setup.settings_hostinger
python manage.py collectstatic --noinput --settings=setup.settings_hostinger
python manage.py create_admin --settings=setup.settings_hostinger
```

### 4. Gunicorn Configuration

#### Create Gunicorn service file:

```bash
nano /etc/systemd/system/innovasus.service
```

```ini
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
```

#### Start Gunicorn service:

```bash
systemctl daemon-reload
systemctl start innovasus
systemctl enable innovasus
systemctl status innovasus
```

### 5. Nginx Configuration

#### Create Nginx site configuration:

```bash
nano /etc/nginx/sites-available/innovasus
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable site:

```bash
ln -s /etc/nginx/sites-available/innovasus /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 6. SSL Certificate (Let's Encrypt)

#### Install Certbot:

```bash
apt install certbot python3-certbot-nginx -y
```

#### Get SSL certificate:

```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 7. File Permissions

#### Set proper permissions:

```bash
chown -R www-data:www-data /var/www/innovasus
chmod -R 755 /var/www/innovasus
```

### 8. Firewall Configuration

#### Configure UFW:

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

## 🔧 Maintenance Commands

### Update application:

```bash
cd /var/www/innovasus
git pull
source venv/bin/activate
pip install -r requirements-hostinger.txt
python manage.py migrate --settings=setup.settings_hostinger
python manage.py collectstatic --noinput --settings=setup.settings_hostinger
systemctl restart innovasus
```

### Check logs:

```bash
journalctl -u innovasus -f
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 🌐 Domain Configuration

1. **Update DNS**: Point your domain A record to your VPS IP
2. **Update settings**: Replace domain placeholders in settings_hostinger.py
3. **Get SSL**: Run certbot after DNS propagation

## 📊 Monitoring

Your Django app will be available at:

- **HTTP**: http://your-domain.com (redirects to HTTPS)
- **HTTPS**: https://your-domain.com
- **Admin**: https://your-domain.com/admin/

## 🆘 Troubleshooting

### Service not starting:

```bash
systemctl status innovasus
journalctl -u innovasus -f
```

### Nginx errors:

```bash
nginx -t
systemctl status nginx
```

### Database issues:

```bash
mysql -u innovasus_user -p innovasus_db
```
