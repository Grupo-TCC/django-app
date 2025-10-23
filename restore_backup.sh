#!/bin/bash

# Quick Database Restore Script
# Restores a previously created backup

set -e

if [ $# -eq 0 ]; then
    echo "📦 Available Backups:"
    echo "==================="
    
    if [ -d "database_backups" ]; then
        for backup in database_backups/*/; do
            if [ -d "$backup" ]; then
                backup_name=$(basename "$backup")
                echo "📁 $backup_name"
                
                if [ -f "$backup/backup_info.txt" ]; then
                    echo "   $(grep "Created:" "$backup/backup_info.txt")"
                fi
                echo ""
            fi
        done
    else
        echo "📭 No backups found"
    fi
    
    echo "Usage: ./restore_backup.sh <backup_name>"
    exit 1
fi

BACKUP_NAME="$1"
BACKUP_DIR="database_backups/$BACKUP_NAME"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup not found: $BACKUP_NAME"
    echo "Available backups:"
    ls -1 database_backups/ 2>/dev/null || echo "  No backups found"
    exit 1
fi

echo "🔄 Restoring backup: $BACKUP_NAME"
echo "================================="

# Show backup info
if [ -f "$BACKUP_DIR/backup_info.txt" ]; then
    echo "📋 Backup Info:"
    cat "$BACKUP_DIR/backup_info.txt"
    echo ""
fi

# Confirm restore
read -p "⚠️  This will replace your current database and media files. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Backup current files before restore
echo "💾 Creating safety backup of current files..."
SAFETY_BACKUP="database_backups/safety_backup_$(date +"%Y%m%d_%H%M%S")"
mkdir -p "$SAFETY_BACKUP"

if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "$SAFETY_BACKUP/db.sqlite3"
    echo "   Current database backed up to: $SAFETY_BACKUP"
fi

if [ -d "media" ]; then
    cp -r media "$SAFETY_BACKUP/media"
    echo "   Current media backed up to: $SAFETY_BACKUP"
fi

# Restore database
if [ -f "$BACKUP_DIR/db.sqlite3" ]; then
    cp "$BACKUP_DIR/db.sqlite3" db.sqlite3
    echo "✅ Database restored"
else
    echo "⚠️  No database file in backup"
fi

# Restore media files
if [ -d "$BACKUP_DIR/media" ]; then
    rm -rf media
    cp -r "$BACKUP_DIR/media" media
    echo "✅ Media files restored"
else
    echo "⚠️  No media files in backup"
fi

echo ""
echo "🎉 Backup restored successfully!"
echo "📁 Safety backup created at: $SAFETY_BACKUP"
echo ""
echo "🔄 You may want to restart your Django server to ensure changes take effect."