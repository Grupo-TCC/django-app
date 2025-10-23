#!/usr/bin/env python3
"""
Database Backup & Restore System
This script helps you create, manage, and restore database backups
"""

import os
import sys
import shutil
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add Django project to path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

import django
django.setup()

from django.core.management import call_command
from django.conf import settings

class DatabaseBackupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / 'database_backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_timestamped_backup(self, description=""):
        """Create a full backup with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        if description:
            backup_name += f"_{description}"
        
        return self.create_backup(backup_name)
    
    def create_backup(self, backup_name):
        """Create a complete backup (database + media files + fixture)"""
        print(f"📦 Creating backup: {backup_name}")
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        # 1. Copy SQLite database file
        db_backup = self._backup_sqlite_file(backup_path)
        
        # 2. Export Django fixture (JSON format)
        fixture_backup = self._export_django_fixture(backup_path)
        
        # 3. Backup media files
        media_backup = self._backup_media_files(backup_path)
        
        # 4. Create backup info file
        self._create_backup_info(backup_path, {
            'name': backup_name,
            'created': datetime.now().isoformat(),
            'sqlite_file': db_backup,
            'fixture_file': fixture_backup,
            'media_path': media_backup,
            'django_version': django.get_version(),
        })
        
        print(f"✅ Backup created successfully: {backup_path}")
        return backup_path
    
    def _backup_sqlite_file(self, backup_path):
        """Copy the SQLite database file"""
        db_file = Path(settings.DATABASES['default']['NAME'])
        if db_file.exists():
            backup_db = backup_path / 'db.sqlite3'
            shutil.copy2(db_file, backup_db)
            print(f"  📄 SQLite file backed up: {backup_db}")
            return str(backup_db)
        else:
            print("  ⚠️  SQLite file not found")
            return None
    
    def _export_django_fixture(self, backup_path):
        """Export Django data as JSON fixture"""
        fixture_file = backup_path / 'data_fixture.json'
        
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
            print(f"  📋 Django fixture exported: {fixture_file}")
            return str(fixture_file)
        except Exception as e:
            print(f"  ❌ Error exporting fixture: {e}")
            return None
    
    def _backup_media_files(self, backup_path):
        """Backup media files"""
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists() and any(media_root.iterdir()):
            media_backup = backup_path / 'media'
            shutil.copytree(media_root, media_backup, dirs_exist_ok=True)
            print(f"  📁 Media files backed up: {media_backup}")
            return str(media_backup)
        else:
            print("  ⚠️  No media files to backup")
            return None
    
    def _create_backup_info(self, backup_path, info):
        """Create backup information file"""
        info_file = backup_path / 'backup_info.json'
        with open(info_file, 'w') as f:
            json.dump(info, f, indent=2)
        print(f"  📋 Backup info saved: {info_file}")
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                info_file = backup_dir / 'backup_info.json'
                if info_file.exists():
                    with open(info_file) as f:
                        info = json.load(f)
                    backups.append({
                        'path': backup_dir,
                        'info': info
                    })
                else:
                    # Legacy backup without info file
                    backups.append({
                        'path': backup_dir,
                        'info': {
                            'name': backup_dir.name,
                            'created': 'Unknown',
                            'sqlite_file': str(backup_dir / 'db.sqlite3') if (backup_dir / 'db.sqlite3').exists() else None
                        }
                    })
        
        # Sort by creation date
        backups.sort(key=lambda x: x['info'].get('created', ''), reverse=True)
        return backups
    
    def restore_backup(self, backup_name):
        """Restore a backup"""
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        print(f"🔄 Restoring backup: {backup_name}")
        
        # 1. Restore SQLite file
        self._restore_sqlite_file(backup_path)
        
        # 2. Restore media files
        self._restore_media_files(backup_path)
        
        print(f"✅ Backup restored successfully: {backup_name}")
        return True
    
    def _restore_sqlite_file(self, backup_path):
        """Restore SQLite database file"""
        backup_db = backup_path / 'db.sqlite3'
        if backup_db.exists():
            current_db = Path(settings.DATABASES['default']['NAME'])
            
            # Create backup of current database
            if current_db.exists():
                current_backup = current_db.with_suffix('.backup')
                shutil.copy2(current_db, current_backup)
                print(f"  💾 Current database backed up to: {current_backup}")
            
            # Restore backup
            shutil.copy2(backup_db, current_db)
            print(f"  📄 SQLite database restored")
        else:
            print("  ⚠️  No SQLite file in backup")
    
    def _restore_media_files(self, backup_path):
        """Restore media files"""
        backup_media = backup_path / 'media'
        if backup_media.exists():
            media_root = Path(settings.MEDIA_ROOT)
            
            # Create backup of current media
            if media_root.exists():
                media_backup = media_root.with_suffix('.backup')
                if media_backup.exists():
                    shutil.rmtree(media_backup)
                shutil.copytree(media_root, media_backup)
                print(f"  💾 Current media backed up to: {media_backup}")
            
            # Restore backup media
            if media_root.exists():
                shutil.rmtree(media_root)
            shutil.copytree(backup_media, media_root)
            print(f"  📁 Media files restored")
        else:
            print("  ⚠️  No media files in backup")

def main():
    """Main backup management interface"""
    manager = DatabaseBackupManager()
    
    if len(sys.argv) < 2:
        print("📦 Database Backup Manager")
        print("=" * 40)
        print("Usage:")
        print("  python backup_manager.py create [description]  - Create new backup")
        print("  python backup_manager.py list                 - List all backups")
        print("  python backup_manager.py restore <name>       - Restore backup")
        print("  python backup_manager.py quick                - Quick backup with timestamp")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        manager.create_timestamped_backup(description)
    
    elif command == 'quick':
        manager.create_timestamped_backup("quick_backup")
    
    elif command == 'list':
        backups = manager.list_backups()
        if not backups:
            print("📭 No backups found")
            return
        
        print("📦 Available Backups:")
        print("=" * 60)
        for backup in backups:
            info = backup['info']
            print(f"Name: {info['name']}")
            print(f"Created: {info.get('created', 'Unknown')}")
            print(f"Path: {backup['path']}")
            if info.get('sqlite_file'):
                print(f"SQLite: ✅")
            if info.get('fixture_file'):
                print(f"Fixture: ✅")
            if info.get('media_path'):
                print(f"Media: ✅")
            print("-" * 40)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Please specify backup name to restore")
            return
        
        backup_name = sys.argv[2]
        
        # Confirm restore
        print(f"⚠️  This will replace your current database and media files!")
        response = input(f"Are you sure you want to restore '{backup_name}'? (y/N): ")
        
        if response.lower() == 'y':
            manager.restore_backup(backup_name)
        else:
            print("❌ Restore cancelled")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()