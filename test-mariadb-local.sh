#!/bin/bash

# Local MariaDB Testing Script
# Test your Django app with MariaDB locally before AWS deployment

set -e

echo "🧪 Local MariaDB Testing Setup"
echo "============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker is available"

# Create local testing environment
echo "🐳 Starting MariaDB container..."

# Use docker-compose to start MariaDB
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

$COMPOSE_CMD up -d db

echo "⏳ Waiting for MariaDB to start..."
sleep 10

# Test MariaDB connection
echo "🔌 Testing MariaDB connection..."
if docker exec django-app-db-1 mysql -u admin -padminpassword -e "SELECT 1;" &>/dev/null; then
    echo "✅ MariaDB is running and accessible"
else
    echo "❌ MariaDB connection failed"
    echo "Checking logs..."
    $COMPOSE_CMD logs db
    exit 1
fi

# Create local environment for testing
echo "⚙️ Creating local test environment..."
cat > .env.local << EOF
# Local MariaDB Testing Environment
DEBUG=True
SECRET_KEY=local-testing-secret-key-not-for-production

# Local MariaDB (Docker)
DB_NAME=django_db
DB_USER=admin
DB_PASSWORD=adminpassword
DB_HOST=127.0.0.1
DB_PORT=3306

# Email (optional for testing)
GMAIL_APP_PASSWORD=your-gmail-app-password
EOF

# Test Django with MariaDB
echo "🧪 Testing Django with MariaDB..."

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Copy environment variables
cp .env.local .env

# Test database connection
echo "🔄 Testing Django database connection..."
if python manage.py check --database default --settings=setup.settings_production; then
    echo "✅ Django can connect to MariaDB"
else
    echo "❌ Django cannot connect to MariaDB"
    exit 1
fi

# Run migrations
echo "🔄 Running migrations on MariaDB..."
python manage.py migrate --settings=setup.settings_production

# Import data from SQLite backup
echo "📥 Importing data from SQLite backup..."
if [ -f "database_backups/backup_*/data_fixture.json" ]; then
    FIXTURE_FILE=$(ls database_backups/backup_*/data_fixture.json | head -1)
    echo "Using fixture: $FIXTURE_FILE"
    python manage.py loaddata "$FIXTURE_FILE" --settings=setup.settings_production
    echo "✅ Data imported successfully"
else
    echo "⚠️  No SQLite backup found. Creating a fresh database."
    echo "You can import data later using:"
    echo "  python manage.py loaddata <fixture_file> --settings=setup.settings_production"
fi

# Test the application
echo "🚀 Starting Django with MariaDB..."
echo "Visit: http://127.0.0.1:8000/feed/traducao/"
echo ""
echo "📋 Testing Commands:"
echo "  - Check app: curl -I http://127.0.0.1:8000/"
echo "  - Admin: http://127.0.0.1:8000/admin/"
echo "  - Stop MariaDB: $COMPOSE_CMD down"
echo "  - Restart MariaDB: $COMPOSE_CMD up -d db"
echo ""
echo "🗄️ Database Commands:"
echo "  - Connect to DB: docker exec -it django-app-db-1 mysql -u admin -padminpassword django_db"
echo "  - View tables: python manage.py dbshell --settings=setup.settings_production"
echo ""
echo "Press Ctrl+C to stop the Django server..."

# Start Django server
python manage.py runserver --settings=setup.settings_production