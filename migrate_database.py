#!/usr/bin/env python3
"""
Database Migration Script: SQLite to MariaDB
This script helps migrate data from SQLite to MariaDB
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add Django project to path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

import django
django.setup()

from django.core.management import call_command
from django.conf import settings

def export_sqlite_data():
    """Export data from SQLite database"""
    print("📤 Exporting data from SQLite...")
    
    # Create backup directory
    backup_dir = Path('database_backup')
    backup_dir.mkdir(exist_ok=True)
    
    # Export data using Django's dumpdata command
    fixture_file = backup_dir / 'data_backup.json'
    
    try:
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
        print(f"✅ Data exported to: {fixture_file}")
        return fixture_file
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return None

def backup_media_files():
    """Backup media files"""
    print("📁 Backing up media files...")
    
    media_root = Path(settings.MEDIA_ROOT)
    backup_dir = Path('database_backup/media')
    
    if media_root.exists():
        try:
            subprocess.run([
                'cp', '-r', str(media_root), str(backup_dir)
            ], check=True)
            print(f"✅ Media files backed up to: {backup_dir}")
            return backup_dir
        except subprocess.CalledProcessError as e:
            print(f"❌ Error backing up media files: {e}")
            return None
    else:
        print("⚠️  No media files found to backup")
        return None

def import_to_mariadb(fixture_file):
    """Import data to MariaDB database"""
    print("📥 Importing data to MariaDB...")
    
    if not fixture_file or not fixture_file.exists():
        print("❌ No fixture file found for import")
        return False
    
    try:
        # Set production settings for MariaDB
        os.environ['DJANGO_SETTINGS_MODULE'] = 'setup.settings_production'
        
        # Run migrations first
        print("🔄 Running database migrations...")
        call_command('migrate', '--settings=setup.settings_production')
        
        # Load data
        print("📥 Loading data...")
        call_command('loaddata', str(fixture_file), '--settings=setup.settings_production')
        
        print("✅ Data successfully imported to MariaDB")
        return True
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        return False

def main():
    """Main migration process"""
    print("🚀 Starting database migration from SQLite to MariaDB...")
    print("=" * 60)
    
    # Step 1: Export SQLite data
    fixture_file = export_sqlite_data()
    if not fixture_file:
        print("❌ Migration failed: Could not export SQLite data")
        return
    
    # Step 2: Backup media files
    backup_media_files()
    
    # Step 3: Import to MariaDB (requires production settings)
    print("\n🔄 Ready to import to MariaDB...")
    print("⚠️  Make sure your MariaDB database is running and configured in .env")
    
    response = input("Continue with import to MariaDB? (y/N): ")
    if response.lower() == 'y':
        success = import_to_mariadb(fixture_file)
        if success:
            print("\n🎉 Migration completed successfully!")
            print("📋 Post-migration checklist:")
            print("  - Test your application thoroughly")
            print("  - Update any remaining hardcoded SQLite references")
            print("  - Consider removing the old SQLite database file")
        else:
            print("\n❌ Migration failed during import phase")
    else:
        print("📋 Export completed. Import when ready by running:")
        print(f"   python manage.py loaddata {fixture_file} --settings=setup.settings_production")

if __name__ == '__main__':
    main()