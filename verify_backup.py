#!/usr/bin/env python3
"""
Backup Verification Script
Verifies the integrity and completeness of database backups
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Add Django project to path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

import django
django.setup()

from django.core.management import call_command
from django.conf import settings

def verify_backup(backup_name):
    """Verify a backup's integrity and completeness"""
    backup_dir = Path('database_backups') / backup_name
    
    if not backup_dir.exists():
        print(f"❌ Backup not found: {backup_name}")
        return False
    
    print(f"🔍 Verifying backup: {backup_name}")
    print("=" * 50)
    
    verification_passed = True
    
    # Check backup info
    info_file = backup_dir / 'backup_info.json'
    if info_file.exists():
        with open(info_file) as f:
            info = json.load(f)
        print(f"📋 Backup Info:")
        print(f"   Name: {info.get('name', 'Unknown')}")
        print(f"   Created: {info.get('created', 'Unknown')}")
        print(f"   Django Version: {info.get('django_version', 'Unknown')}")
    else:
        print("⚠️  No backup info file found")
        verification_passed = False
    
    # Check SQLite file
    sqlite_file = backup_dir / 'db.sqlite3'
    if sqlite_file.exists():
        try:
            # Test SQLite file integrity
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()
            conn.close()
            
            if result[0] == 'ok':
                print(f"✅ SQLite file: Valid ({sqlite_file.stat().st_size} bytes)")
            else:
                print(f"❌ SQLite file: Integrity check failed")
                verification_passed = False
        except Exception as e:
            print(f"❌ SQLite file: Error - {e}")
            verification_passed = False
    else:
        print("❌ SQLite file: Missing")
        verification_passed = False
    
    # Check fixture file
    fixture_file = backup_dir / 'data_fixture.json'
    if fixture_file.exists():
        try:
            with open(fixture_file) as f:
                data = json.load(f)
            print(f"✅ Fixture file: Valid ({len(data)} records, {fixture_file.stat().st_size} bytes)")
        except Exception as e:
            print(f"❌ Fixture file: Error - {e}")
            verification_passed = False
    else:
        print("❌ Fixture file: Missing")
        verification_passed = False
    
    # Check media files
    media_dir = backup_dir / 'media'
    if media_dir.exists():
        media_count = sum(1 for _ in media_dir.rglob('*') if _.is_file())
        media_size = sum(f.stat().st_size for f in media_dir.rglob('*') if f.is_file())
        print(f"✅ Media files: {media_count} files ({media_size} bytes)")
    else:
        print("⚠️  Media files: No media directory (might be empty)")
    
    print("\n" + "=" * 50)
    if verification_passed:
        print(f"✅ Backup verification PASSED: {backup_name}")
        print("🎉 This backup is ready for restore or migration!")
    else:
        print(f"❌ Backup verification FAILED: {backup_name}")
        print("⚠️  This backup may be incomplete or corrupted!")
    
    return verification_passed

def verify_all_backups():
    """Verify all available backups"""
    backup_dir = Path('database_backups')
    if not backup_dir.exists():
        print("📭 No backup directory found")
        return
    
    backups = [d for d in backup_dir.iterdir() if d.is_dir()]
    if not backups:
        print("📭 No backups found")
        return
    
    print(f"🔍 Verifying {len(backups)} backup(s)...")
    print("\n")
    
    passed = 0
    for backup in backups:
        if verify_backup(backup.name):
            passed += 1
        print("\n")
    
    print(f"📊 Summary: {passed}/{len(backups)} backups passed verification")

def main():
    """Main verification interface"""
    if len(sys.argv) < 2:
        print("🔍 Backup Verification Tool")
        print("=" * 30)
        print("Usage:")
        print("  python verify_backup.py <backup_name>  - Verify specific backup")
        print("  python verify_backup.py all            - Verify all backups")
        return
    
    if sys.argv[1].lower() == 'all':
        verify_all_backups()
    else:
        verify_backup(sys.argv[1])

if __name__ == '__main__':
    main()