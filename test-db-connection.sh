#!/bin/bash

# Database Connection Test Script
echo "Testing database connection..."

DB_HOST="django-mariadb.c8pgiy0imd9p.us-east-1.rds.amazonaws.com"
DB_USER="admin"
DB_PASS="[YOUR_DB_PASSWORD_HERE]"
DB_NAME="django_db"

echo "Testing MySQL connection..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS -e "SELECT 'Connection successful!' as Status, VERSION() as Version;"

echo ""
echo "Testing if database exists..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS -e "SHOW DATABASES;" | grep django_db

echo ""
echo "Database connection details:"
echo "Host: $DB_HOST"
echo "User: $DB_USER"
echo "Database: $DB_NAME"
echo "Port: 3306"