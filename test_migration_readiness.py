#!/usr/bin/env python3
"""
MariaDB Migration Test (No Docker Required)
Tests the Django configuration and data export for MariaDB migration
"""

import os
import sys
import subprocess
from pathlib import Path

# Add Django project to path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

print("🧪 MariaDB Migration Test (No Docker)")
print("=" * 40)

def test_sqlite_current_state():
    """Test current SQLite database"""
    print("📊 Testing current SQLite database...")
    
    try:
        import django
        django.setup()
        
        from django.core.management import call_command
        from django.db import connection
        
        # Test current database
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ SQLite tables found: {len(tables)}")
            
        # Test Django models
        from user.models import User
        from feed.models import Media, MediaFile
        
        user_count = User.objects.count()
        media_count = Media.objects.count()
        media_file_count = MediaFile.objects.count()
        
        print(f"✅ Users: {user_count}")
        print(f"✅ Media posts: {media_count}")
        print(f"✅ Media files: {media_file_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        return False

def test_mariadb_settings():
    """Test MariaDB production settings"""
    print("\n⚙️ Testing MariaDB settings configuration...")
    
    try:
        # Test production settings import
        import setup.settings_production
        
        # Check database configuration
        databases = setup.settings_production.DATABASES
        db_config = databases['default']
        
        print(f"✅ Database engine: {db_config['ENGINE']}")
        print(f"✅ Database configured for: MariaDB/MySQL")
        
        if db_config['ENGINE'] == 'django.db.backends.mysql':
            print("✅ MariaDB settings are correctly configured")
            return True
        else:
            print("❌ Database engine not set to MySQL/MariaDB")
            return False
            
    except Exception as e:
        print(f"❌ MariaDB settings test failed: {e}")
        return False

def test_requirements():
    """Test if MariaDB requirements are installed"""
    print("\n📦 Testing MariaDB Python packages...")
    
    required_packages = ['mysqlclient', 'PyMySQL']
    installed = []
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            installed.append(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}: Missing")
    
    if missing:
        print(f"\n📋 To install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    else:
        print("✅ All MariaDB packages are installed")
        return True

def export_test_data():
    """Export current data for migration testing"""
    print("\n📤 Exporting current data for migration test...")
    
    try:
        import django
        django.setup()
        
        from django.core.management import call_command
        
        # Create test export directory
        test_dir = Path('migration_test')
        test_dir.mkdir(exist_ok=True)
        
        # Export current data
        fixture_file = test_dir / 'test_data.json'
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--exclude=contenttypes',
            '--exclude=auth.Permission',
            '--exclude=sessions',
            '--indent=2',
            output=str(fixture_file)
        )
        
        print(f"✅ Test data exported to: {fixture_file}")
        print(f"📊 File size: {fixture_file.stat().st_size} bytes")
        
        return fixture_file
        
    except Exception as e:
        print(f"❌ Data export failed: {e}")
        return None

def create_test_mariadb_env():
    """Create test environment file for MariaDB"""
    print("\n⚙️ Creating test MariaDB environment...")
    
    env_content = """# Test MariaDB Environment
# Use this when you have MariaDB running (local or AWS)

DEBUG=True
SECRET_KEY=test-mariadb-secret-key-not-for-production

# MariaDB Configuration (update with your actual values)
DB_NAME=django_db_test
DB_USER=admin
DB_PASSWORD=your_password_here
DB_HOST=127.0.0.1  # or your RDS endpoint
DB_PORT=3306

# Email (optional for testing)
GMAIL_APP_PASSWORD=your-gmail-app-password
"""
    
    env_file = Path('.env.mariadb_test')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Test environment created: {env_file}")
    print("📋 Edit this file with your MariaDB connection details")
    
    return env_file

def main():
    """Run all tests"""
    print("🚀 Starting Django → MariaDB migration tests...")
    print()
    
    # Test 1: Current SQLite state
    sqlite_ok = test_sqlite_current_state()
    
    # Test 2: MariaDB settings
    settings_ok = test_mariadb_settings()
    
    # Test 3: Required packages
    packages_ok = test_requirements()
    
    # Test 4: Data export
    export_file = export_test_data()
    
    # Test 5: Environment setup
    env_file = create_test_mariadb_env()
    
    print("\n" + "=" * 50)
    print("📊 Migration Test Summary")
    print("=" * 50)
    
    print(f"SQLite Database: {'✅ Ready' if sqlite_ok else '❌ Issues'}")
    print(f"MariaDB Settings: {'✅ Configured' if settings_ok else '❌ Issues'}")
    print(f"Required Packages: {'✅ Installed' if packages_ok else '❌ Missing'}")
    print(f"Data Export: {'✅ Success' if export_file else '❌ Failed'}")
    print(f"Environment File: {'✅ Created' if env_file else '❌ Failed'}")
    
    if sqlite_ok and settings_ok and packages_ok and export_file:
        print("\n🎉 Migration Test PASSED!")
        print("✅ Your application is ready for MariaDB migration")
        print()
        print("📋 Next Steps:")
        print("1. Set up MariaDB (Docker, local install, or AWS RDS)")
        print("2. Update .env.mariadb_test with your database credentials")
        print("3. Test with: python manage.py migrate --settings=setup.settings_production")
        print("4. Import data: python manage.py loaddata migration_test/test_data.json --settings=setup.settings_production")
        
        if not packages_ok:
            print("\n⚠️  Install missing packages first:")
            print("pip install mysqlclient PyMySQL")
    else:
        print("\n❌ Migration Test FAILED!")
        print("Please fix the issues above before proceeding with migration")
    
    print()
    print("🐳 To use Docker for local testing:")
    print("   brew install --cask docker")
    print("   ./test-mariadb-local.sh")

if __name__ == '__main__':
    main()