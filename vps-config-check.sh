#!/bin/bash

# InnovaSUS VPS Configuration Validator
# Run this to verify all files are correctly configured for VPS deployment

echo "🔍 InnovaSUS VPS Configuration Validation"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "1. 📁 Core Configuration Files"
echo "=============================="

# Check settings_hostinger.py
if [ -f "setup/settings_hostinger.py" ]; then
    print_ok "settings_hostinger.py exists"
    
    if grep -q "VPS" setup/settings_hostinger.py; then
        print_ok "Configured for VPS deployment"
    else
        print_warning "Check VPS configuration in settings"
    fi
    
    if grep -q "innovasusbr.com" setup/settings_hostinger.py; then
        print_ok "Domain configured (innovasusbr.com)"
    else
        print_error "Domain not configured"
    fi
else
    print_error "settings_hostinger.py missing"
fi

# Check wsgi.py
if [ -f "setup/wsgi.py" ]; then
    print_ok "wsgi.py exists"
    
    if grep -q "settings_hostinger" setup/wsgi.py; then
        print_ok "WSGI configured for production settings"
    else
        print_error "WSGI not configured for production"
    fi
else
    print_error "wsgi.py missing"
fi

# Check requirements
if [ -f "requirements-hostinger.txt" ]; then
    print_ok "requirements-hostinger.txt exists"
    
    if grep -q "mysqlclient" requirements-hostinger.txt; then
        print_ok "MySQL client configured"
    else
        print_error "MySQL client missing"
    fi
    
    if grep -q "gunicorn" requirements-hostinger.txt; then
        print_ok "Gunicorn configured"
    else
        print_error "Gunicorn missing"
    fi
else
    print_error "requirements-hostinger.txt missing"
fi

echo ""
echo "2. 🚀 Deployment Scripts"
echo "======================="

# Check deployment script
if [ -f "deploy-hostinger.sh" ]; then
    print_ok "deploy-hostinger.sh exists"
    
    if [ -x "deploy-hostinger.sh" ]; then
        print_ok "Deployment script is executable"
    else
        print_warning "Run: chmod +x deploy-hostinger.sh"
    fi
    
    if grep -q "VPS" deploy-hostinger.sh; then
        print_ok "Script configured for VPS"
    else
        print_warning "Check VPS configuration in script"
    fi
else
    print_error "deploy-hostinger.sh missing"
fi

# Check setup script
if [ -f "vps-setup.sh" ]; then
    print_ok "vps-setup.sh exists"
    
    if [ -x "vps-setup.sh" ]; then
        print_ok "Setup script is executable"
    else
        print_warning "Run: chmod +x vps-setup.sh"
    fi
else
    print_error "vps-setup.sh missing"
fi

# Check diagnostics script
if [ -f "vps-diagnostics.sh" ]; then
    print_ok "vps-diagnostics.sh exists"
    
    if [ -x "vps-diagnostics.sh" ]; then
        print_ok "Diagnostics script is executable"
    else
        print_warning "Run: chmod +x vps-diagnostics.sh"
    fi
else
    print_error "vps-diagnostics.sh missing"
fi

echo ""
echo "3. 📖 Documentation"
echo "=================="

if [ -f "VPS_DEPLOYMENT_GUIDE.md" ]; then
    print_ok "VPS deployment guide exists"
else
    print_error "VPS_DEPLOYMENT_GUIDE.md missing"
fi

echo ""
echo "4. 🐍 Django Configuration"
echo "=========================="

# Check Django files
if [ -f "manage.py" ]; then
    print_ok "Django project structure correct"
else
    print_error "manage.py missing - not a Django project"
fi

# Check apps
if [ -d "feed" ] && [ -d "user" ]; then
    print_ok "Django apps (feed, user) present"
else
    print_error "Django apps missing"
fi

# Check templates
if [ -d "templates" ]; then
    print_ok "Templates directory exists"
    
    if [ -f "templates/base.html" ]; then
        print_ok "Base template exists"
        
        if grep -q "mobile-responsive.css" templates/base.html; then
            print_ok "Mobile responsive CSS included"
        else
            print_warning "Mobile CSS not found in base template"
        fi
    else
        print_error "Base template missing"
    fi
else
    print_error "Templates directory missing"
fi

# Check static files
if [ -d "static" ]; then
    print_ok "Static files directory exists"
    
    if [ -f "static/styles/mobile-responsive.css" ]; then
        print_ok "Mobile responsive CSS exists"
    else
        print_error "Mobile responsive CSS missing"
    fi
else
    print_error "Static files directory missing"
fi

echo ""
echo "5. 🎯 VPS-Specific Validations"
echo "============================="

# Check if passenger_wsgi.py is VPS-ready (should not have shared hosting paths)
if [ -f "passenger_wsgi.py" ]; then
    if grep -q "/home/u.*public_html" passenger_wsgi.py; then
        print_error "passenger_wsgi.py still has shared hosting paths"
    else
        print_ok "passenger_wsgi.py configured for VPS"
    fi
fi

# Check settings for VPS-specific configurations
if grep -q "pymysql.install_as_MySQLdb" setup/settings_hostinger.py 2>/dev/null; then
    print_warning "pymysql.install_as_MySQLdb found - this is for shared hosting"
    print_info "Consider removing for VPS deployment"
fi

echo ""
echo "📋 Summary"
echo "=========="

print_info "Ready for VPS deployment with these commands:"
echo ""
echo "   # On your VPS:"
echo "   wget https://raw.githubusercontent.com/Grupo-TCC/django-app/master/vps-setup.sh"
echo "   chmod +x vps-setup.sh && sudo ./vps-setup.sh"
echo ""
print_info "Your app will be live at: https://innovasusbr.com"
echo ""