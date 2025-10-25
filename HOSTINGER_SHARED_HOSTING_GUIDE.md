# InnovaSUS - Hostinger Shared Hosting Deployment

## 🌐 **Deploy Django to Hostinger Shared Hosting**

### **Requirements:**

- Hostinger Shared Hosting with Python support
- Domain: innovasusbr.com
- MySQL database access
- File Manager or FTP access

## 📋 **Deployment Steps**

### **Step 1: Prepare Your Django App**

1. **Create requirements.txt for shared hosting:**

```
Django==5.0.6
gunicorn==21.2.0
mysql-connector-python==8.3.0
PyMySQL==1.1.0
django-cors-headers==4.3.1
Pillow==10.2.0
whitenoise==6.6.0
```

2. **Create passenger_wsgi.py (Hostinger specific):**

```python
import os
import sys

# Add your project directory to Python path
project_home = '/home/u123456789/domains/innovasusbr.com/public_html'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'setup.settings_hostinger'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

3. **Update settings_hostinger.py for shared hosting:**

```python
import os
from pathlib import Path
import pymysql

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DEBUG = False
ALLOWED_HOSTS = ['innovasusbr.com', 'www.innovasusbr.com', '*.hostinger.com']

# Database for Hostinger shared hosting
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'u123456789_innovasus'),
        'USER': os.environ.get('DB_USER', 'u123456789_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your-db-password'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Static files for shared hosting
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'innovasus76@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://innovasusbr.com",
    "https://www.innovasusbr.com",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'corsheaders',
    'feed',
    'user',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'setup.urls'
AUTH_USER_MODEL = 'user.User'
```

### **Step 2: Deploy to Hostinger**

1. **Access File Manager:**

   - Go to Hostinger hPanel
   - Open File Manager
   - Navigate to `domains/innovasusbr.com/public_html`

2. **Upload your project:**

   - Compress your Django project as .zip
   - Upload via File Manager
   - Extract in public_html directory

3. **Set up database:**

   - Go to MySQL Databases in hPanel
   - Create database (note the full name like u123456789_innovasus)
   - Create user and assign to database
   - Update settings_hostinger.py with real credentials

4. **Install dependencies:**

   - Access Terminal (if available) or contact support
   - Run: `pip install -r requirements.txt --user`

5. **Run migrations:**
   ```bash
   python manage.py migrate --settings=setup.settings_hostinger
   python manage.py collectstatic --settings=setup.settings_hostinger
   ```

### **Step 3: Configure Domain**

1. **Point domain to hosting:**

   - In hPanel, go to Domains
   - Make sure innovasusbr.com points to your hosting
   - Check DNS settings

2. **SSL Certificate:**
   - Enable SSL in hPanel
   - Use free Let's Encrypt certificate

### **Step 4: Test Your Application**

Visit: https://innovasusbr.com

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Python Path Issues:**

   - Make sure passenger_wsgi.py has correct paths
   - Check that Python version matches requirements

2. **Database Connection:**

   - Verify database credentials
   - Check database name format (usually u123456789_dbname)

3. **Static Files:**

   - Run collectstatic command
   - Check STATIC_ROOT permissions

4. **Permissions:**
   - Set proper file permissions (755 for directories, 644 for files)
   - Check media upload permissions

## 📞 **Support**

If you encounter issues:

- Contact Hostinger support for Python app deployment help
- Check error logs in hPanel
- Verify all settings match your account details

## ✅ **Success Checklist**

- [ ] Files uploaded to public_html
- [ ] Database created and configured
- [ ] Dependencies installed
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Domain pointing to hosting
- [ ] SSL certificate active
- [ ] Site accessible at innovasusbr.com
