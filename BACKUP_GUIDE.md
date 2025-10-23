# 📦 Database Backup & Migration Guide

## 🎯 Overview

This guide covers how to backup, restore, and migrate your Django database from SQLite to MariaDB while preserving all your data for testing and rollback purposes.

## 📋 Quick Reference

### Backup Commands

```bash
# Quick backup (simplest method)
./quick_backup.sh

# Advanced backup with description
python backup_manager.py create "before_new_feature"

# List all backups
python backup_manager.py list
```

### Restore Commands

```bash
# Quick restore
./restore_backup.sh backup_name

# Advanced restore
python backup_manager.py restore backup_name
```

## 🔄 Migration Workflow

### Phase 1: Create Pre-Migration Backup ✅

```bash
# Already completed - you have a backup at:
# database_backups/backup_20251020_171413_pre_migration_backup/
```

### Phase 2: Test MariaDB Connection (Optional)

```bash
# Test with Docker locally
docker-compose up -d db
python manage.py migrate --settings=setup.settings_production
```

### Phase 3: Migrate to Production

```bash
# Export data for migration
python migrate_database.py

# Deploy to AWS (see AWS deployment guide)
```

## 📁 Backup Structure

Each backup contains:

- **db.sqlite3** - Exact copy of your SQLite database
- **data_fixture.json** - Django fixture (portable format)
- **media/** - All uploaded files (videos, images, PDFs)
- **backup_info.json** - Backup metadata

## 🛠️ Available Tools

### 1. Quick Backup Script (`quick_backup.sh`)

- **Purpose**: Fast backup for daily use
- **Usage**: `./quick_backup.sh`
- **Creates**: Timestamped backup with essential files

### 2. Advanced Backup Manager (`backup_manager.py`)

- **Purpose**: Full-featured backup management
- **Usage**:
  ```bash
  python backup_manager.py create [description]
  python backup_manager.py list
  python backup_manager.py restore <name>
  ```
- **Features**: Detailed metadata, Django fixtures, restoration safety

### 3. Migration Script (`migrate_database.py`)

- **Purpose**: Migrate from SQLite to MariaDB
- **Usage**: `python migrate_database.py`
- **Features**: Export, import, validation

### 4. Restore Scripts

- **Quick**: `./restore_backup.sh <backup_name>`
- **Advanced**: `python backup_manager.py restore <backup_name>`

## 💡 Best Practices

### Before Any Major Changes

```bash
# Create a descriptive backup
python backup_manager.py create "before_video_feature_update"
```

### Weekly Testing Backup

```bash
# Quick weekly backup
./quick_backup.sh
```

### Before Migration

```bash
# Comprehensive pre-migration backup (already done)
python backup_manager.py create "pre_migration_backup"
```

## 🔐 Safety Features

1. **Automatic Safety Backups**: Restore operations create safety backups
2. **Non-Destructive**: Original files preserved during operations
3. **Verification**: Backup integrity checking
4. **Multiple Formats**: Both binary (SQLite) and portable (JSON) formats

## 📋 Testing Your Current Backup

```bash
# List available backups
python backup_manager.py list

# Test restore (creates safety backup automatically)
python backup_manager.py restore backup_20251020_171413_pre_migration_backup
```

## 🚀 Next Steps for Migration

1. **Test Locally with MariaDB** (optional):

   ```bash
   docker-compose up -d db
   python manage.py migrate --settings=setup.settings_production
   ```

2. **Setup AWS RDS MariaDB** (see AWS deployment guide)

3. **Run Migration**:

   ```bash
   python migrate_database.py
   ```

4. **Deploy to AWS** (see deployment scripts)

## ⚠️ Important Notes

- **Always backup before migration**
- **Test restore process before migration**
- **Keep multiple backup copies**
- **Backup both database AND media files**
- **Document your backup schedule**

## 🆘 Emergency Recovery

If something goes wrong:

1. **Immediate Rollback**:

   ```bash
   ./restore_backup.sh backup_20251020_171413_pre_migration_backup
   ```

2. **Check Available Backups**:

   ```bash
   ls -la database_backups/
   ```

3. **Manual Recovery** (last resort):
   ```bash
   cp database_backups/backup_*/db.sqlite3 ./db.sqlite3
   cp -r database_backups/backup_*/media ./media
   ```

Your data is now safely backed up and you can proceed with migration confidence! 🎉
