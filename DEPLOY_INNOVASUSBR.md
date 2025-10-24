# InnovaSus Deployment to innovasusbr.com

## 🌐 **Your Domain Setup:**

- **Domain:** innovasusbr.com
- **Platform:** Hostinger VPS
- **Database:** MySQL
- **Web Server:** Nginx + Gunicorn

## 📋 **Pre-Deployment Checklist:**

### 1. **Hostinger VPS Setup:**

- [ ] VPS is running and accessible via SSH
- [ ] Domain `innovasusbr.com` is pointed to your VPS IP
- [ ] You have root/sudo access to the server

### 2. **Domain Configuration:**

Make sure your domain DNS is configured:

```
A Record: @ → Your VPS IP Address
A Record: www → Your VPS IP Address
```

## 🚀 **Quick Deployment Steps:**

### **Option A: Automated Deployment (Recommended)**

1. **Connect to your VPS:**

```bash
ssh root@your-vps-ip
```

2. **Download and run deployment script:**

```bash
wget https://raw.githubusercontent.com/Grupo-TCC/django-app/master/deploy-hostinger.sh
chmod +x deploy-hostinger.sh
sudo ./deploy-hostinger.sh
```

3. **When prompted, enter:**

- Domain: `innovasusbr.com` (default)
- Server IP: `your-vps-ip-address`
- Database details as requested
- Gmail credentials for email functionality

### **Option B: Manual Step-by-Step**

If you prefer manual deployment, follow the complete guide in `HOSTINGER_DEPLOYMENT_GUIDE.md`.

## 🔧 **Configuration Details:**

### **Database Settings:**

```bash
DB_NAME=innovasus_db
DB_USER=innovasus_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=3306
```

### **Email Configuration:**

```bash
EMAIL_HOST_USER=innovasus76@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
```

### **Django Settings:**

```bash
DEBUG=False
SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=setup.settings_hostinger
```

## 📊 **Post-Deployment Verification:**

After deployment, verify these URLs work:

- **Main Site:** https://innovasusbr.com
- **Admin Panel:** https://innovasusbr.com/admin/
- **Registration:** https://innovasusbr.com/register/

### **Admin Access:**

- **Email:** admin@innovasus.com
- **Password:** InnovaAdmin2025!

## 🔍 **Troubleshooting:**

### **Check Services:**

```bash
# Django app status
systemctl status innovasus

# Nginx status
systemctl status nginx

# View logs
journalctl -u innovasus -f
tail -f /var/log/nginx/error.log
```

### **Common Issues:**

1. **Site not loading:** Check if domain DNS has propagated
2. **502 Bad Gateway:** Django service might be down
3. **Static files not loading:** Run collectstatic command
4. **Database errors:** Check MySQL service and credentials

### **Update Application:**

```bash
cd /var/www/innovasus
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=setup.settings_hostinger
python manage.py collectstatic --noinput --settings=setup.settings_hostinger
systemctl restart innovasus
```

## 🎯 **Final Result:**

Your InnovaSus platform will be live at:

- **🌐 Website:** https://innovasusbr.com
- **👨‍💼 Admin:** https://innovasusbr.com/admin/
- **📝 Registration:** https://innovasusbr.com/register/

## 📞 **Support:**

If you encounter issues:

1. Check the logs using the troubleshooting commands
2. Verify DNS propagation at: https://dnschecker.org/
3. Ensure all services are running on your VPS
