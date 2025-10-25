#!/bin/bash

# InnovaSUS - VPS Troubleshooting & Status Check
# Run this if you encounter issues after deployment

echo "🔍 InnovaSUS VPS Diagnostics"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

echo "1. 🌐 Checking System Services..."
echo "================================="

# Check Nginx
if systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx is not running"
    echo "   Fix: sudo systemctl start nginx"
fi

# Check Gunicorn
if systemctl is-active --quiet gunicorn; then
    print_status "Gunicorn is running"
else
    print_error "Gunicorn is not running"
    echo "   Fix: sudo systemctl start gunicorn"
fi

# Check MySQL
if systemctl is-active --quiet mysql; then
    print_status "MySQL is running"
else
    print_error "MySQL is not running"
    echo "   Fix: sudo systemctl start mysql"
fi

echo ""
echo "2. 🔗 Checking Network & Domain..."
echo "==================================="

# Check if port 80 and 443 are open
if ss -tuln | grep -q ':80 '; then
    print_status "Port 80 (HTTP) is open"
else
    print_error "Port 80 (HTTP) is not open"
fi

if ss -tuln | grep -q ':443 '; then
    print_status "Port 443 (HTTPS) is open"
else
    print_error "Port 443 (HTTPS) is not open"
fi

# Check DNS resolution
if nslookup innovasusbr.com | grep -q "Address"; then
    print_status "Domain innovasusbr.com resolves"
    RESOLVED_IP=$(nslookup innovasusbr.com | grep "Address" | tail -1 | awk '{print $2}')
    print_info "Resolved to: $RESOLVED_IP"
else
    print_error "Domain innovasusbr.com does not resolve"
fi

echo ""
echo "3. 📁 Checking Application Files..."
echo "===================================="

if [ -d "/var/www/innovasus" ]; then
    print_status "Application directory exists"
    
    if [ -f "/var/www/innovasus/manage.py" ]; then
        print_status "Django project files found"
    else
        print_error "Django project files missing"
    fi
    
    if [ -f "/var/www/innovasus/.env.production" ]; then
        print_status "Environment configuration exists"
    else
        print_error "Environment configuration missing"
    fi
    
    if [ -d "/var/www/innovasus/venv" ]; then
        print_status "Python virtual environment exists"
    else
        print_error "Python virtual environment missing"
    fi
else
    print_error "Application directory /var/www/innovasus does not exist"
fi

echo ""
echo "4. 🗄️ Checking Database..."
echo "=========================="

# Test database connection
cd /var/www/innovasus 2>/dev/null
if [ $? -eq 0 ] && [ -f "manage.py" ]; then
    source venv/bin/activate 2>/dev/null
    if python manage.py check --settings=setup.settings_hostinger >/dev/null 2>&1; then
        print_status "Database connection successful"
    else
        print_error "Database connection failed"
        echo "   Check database credentials in .env.production"
    fi
else
    print_error "Cannot test database - application not found"
fi

echo ""
echo "5. 🔐 Checking SSL Certificate..."
echo "=================================="

if [ -d "/etc/letsencrypt/live/innovasusbr.com" ]; then
    print_status "SSL certificate exists"
    CERT_EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/innovasusbr.com/cert.pem 2>/dev/null | cut -d= -f2)
    if [ ! -z "$CERT_EXPIRY" ]; then
        print_info "Certificate expires: $CERT_EXPIRY"
    fi
else
    print_error "SSL certificate not found"
    echo "   Run: sudo certbot --nginx -d innovasusbr.com -d www.innovasusbr.com"
fi

echo ""
echo "6. 📊 System Resources..."
echo "========================="

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
print_info "Memory usage: ${MEMORY_USAGE}%"

# Check disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_status "Disk usage: ${DISK_USAGE}%"
else
    print_error "Disk usage high: ${DISK_USAGE}%"
fi

echo ""
echo "🛠️ Common Fixes:"
echo "================"
echo "• Restart all services: sudo systemctl restart nginx gunicorn mysql"
echo "• Check logs: sudo journalctl -u gunicorn -f"
echo "• Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "• Recollect static files: cd /var/www/innovasus && source venv/bin/activate && python manage.py collectstatic --settings=setup.settings_hostinger"
echo "• Re-run migrations: python manage.py migrate --settings=setup.settings_hostinger"
echo ""
echo "📞 Need help? Check the VPS_DEPLOYMENT_GUIDE.md for detailed troubleshooting!"
echo ""