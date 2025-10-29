#!/bin/bash

# InnovaSus Server Restart Script
# Run this script on your server to update and restart the application

set -e

echo "🔄 Restarting InnovaSus application..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Navigate to application directory
APP_DIR="/var/www/innovasus"  # Adjust this path to match your server setup
cd $APP_DIR

print_status "Pulling latest changes from GitHub..."
git pull origin master

print_status "Activating virtual environment..."
source venv/bin/activate || source .venv/bin/activate

print_status "Installing/updating dependencies..."
pip install -r requirements.txt

print_status "Running database migrations..."
python manage.py migrate

print_status "Collecting static files..."
python manage.py collectstatic --noinput

print_status "Restarting Gunicorn via Supervisor..."
 systemctl restart innovasus

print_status "Restarting Nginx..."
sudo systemctl restart nginx

print_status "Checking application status..."
echo ""
echo "Supervisor status:"
sudo supervisorctl status innovasus || echo "Using systemctl instead..."

echo ""
echo "Nginx status:"
sudo systemctl status nginx --no-pager -l

echo ""
print_status "Application restart completed!"
echo "Your changes should now be live at innovasusbr.com"