# InnovaSUS - Hostinger VPS Deployment Guide

## 🚀 **Complete Step-by-Step VPS Deployment**

### **Phase 1: VPS Setup (In Hostinger Panel)**

#### **Step 1: Create/Access VPS**

1. **Go to Hostinger Control Panel**
2. **Access your VPS** (after refund/upgrade from shared hosting)
3. **Choose Operating System:**
   - **Select:** Ubuntu 22.04 LTS (Recommended)
   - **Alternative:** Ubuntu 20.04 LTS
4. **Set root password** (write it down securely!)
5. **Wait for VPS to be ready** (usually 2-5 minutes)

#### **Step 2: Get VPS Details**

From Hostinger panel, note down:

- **VPS IP Address:** (e.g., 123.456.789.012)
- **Root Password:** (that you set)
- **SSH Port:** Usually 22 (default)

---

### **Phase 2: Domain Configuration**

#### **Step 3: Point Domain to VPS**

1. **In Hostinger Control Panel:**

   - Go to **Domains** section
   - Find **innovasusbr.com**
   - Click **Manage DNS**

2. **Update DNS Records:**
   ```
   A Record: @ → YOUR_VPS_IP_ADDRESS
   A Record: www → YOUR_VPS_IP_ADDRESS
   ```
3. **Save changes** (DNS propagation takes 1-24 hours)

---

### **Phase 3: VPS Deployment**

#### **Step 4: Connect to VPS**

```bash
# From your local terminal
ssh root@YOUR_VPS_IP_ADDRESS
```

- Enter your root password when prompted
- Type "yes" when asked about authenticity

#### **Step 5: Download and Run Deployment Script**

```bash
# Update system first
apt update && apt upgrade -y

# Download deployment script
wget https://raw.githubusercontent.com/Grupo-TCC/django-app/master/deploy-hostinger.sh

# Make executable
chmod +x deploy-hostinger.sh

# Run deployment
sudo ./deploy-hostinger.sh
```

#### **Step 6: Follow Script Prompts**

The script will ask for:

1. **Domain name:** `innovasusbr.com` (press Enter for default)
2. **Database password:** Create a secure password
3. **Secret key:** Press Enter to generate automatically
4. **Gmail app password:** Your Gmail app-specific password
5. **Admin username/email:** For Django superuser

---

### **Phase 4: Post-Deployment**

#### **Step 7: Verify Deployment**

1. **Check services:**

   ```bash
   systemctl status nginx
   systemctl status gunicorn
   systemctl status mysql
   ```

2. **Test database:**
   ```bash
   cd /var/www/innovasus
   source venv/bin/activate
   python manage.py check --settings=setup.settings_hostinger
   ```

#### **Step 8: SSL Certificate**

```bash
# Install Certbot (if not done by script)
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d innovasusbr.com -d www.innovasusbr.com
```

#### **Step 9: Final Tests**

1. **Visit:** https://innovasusbr.com
2. **Test registration:** Create a test account
3. **Test login:** Verify authentication works
4. **Test admin:** Visit https://innovasusbr.com/admin
5. **Test mobile:** Check responsive design on phone

---

### **Phase 5: Troubleshooting**

#### **Common Issues & Solutions:**

1. **502 Bad Gateway:**

   ```bash
   systemctl restart gunicorn
   systemctl restart nginx
   ```

2. **Database Connection Error:**

   ```bash
   systemctl status mysql
   mysql -u root -p
   # Check database exists and user has permissions
   ```

3. **Static Files Not Loading:**

   ```bash
   cd /var/www/innovasus
   source venv/bin/activate
   python manage.py collectstatic --settings=setup.settings_hostinger
   ```

4. **Check Application Logs:**
   ```bash
   tail -f /var/log/nginx/error.log
   tail -f /var/log/nginx/access.log
   journalctl -u gunicorn -f
   ```

---

### **Phase 6: Maintenance**

#### **Regular Maintenance Commands:**

```bash
# Update system
apt update && apt upgrade -y

# Restart services
systemctl restart gunicorn nginx

# Check disk space
df -h

# Check memory usage
free -h

# Backup database
mysqldump -u innovasus_user -p innovasus_db > backup_$(date +%Y%m%d).sql
```

---

## 🎯 **Expected Timeline:**

- **VPS Setup:** 5-10 minutes
- **DNS Configuration:** 5 minutes (propagation: 1-24 hours)
- **Deployment Script:** 10-15 minutes
- **SSL Certificate:** 2-3 minutes
- **Testing & Verification:** 10 minutes

**Total: ~30-45 minutes** (excluding DNS propagation)

---

## ✅ **Success Indicators:**

- [ ] VPS accessible via SSH
- [ ] Domain points to VPS IP
- [ ] Deployment script completes successfully
- [ ] https://innovasusbr.com loads your Django app
- [ ] SSL certificate is active (green padlock)
- [ ] Registration/login works
- [ ] Admin panel accessible
- [ ] Mobile responsive design works

---

## 🆘 **Need Help?**

- **Deployment Issues:** Check logs and restart services
- **DNS Problems:** Wait for propagation or contact Hostinger
- **SSL Issues:** Re-run certbot command
- **App Errors:** Check Django logs and database connection

Your InnovaSUS app will be live at **https://innovasusbr.com**! 🌐✨
