#!/bin/bash

# Quick Database Backup Script
# Creates a timestamped backup of your current database and media files

set -e

echo "📦 Quick Database Backup"
echo "======================="

# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="backup_${TIMESTAMP}"

# Create backup directory
BACKUP_DIR="database_backups/${BACKUP_NAME}"
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backup directory: $BACKUP_DIR"

# Backup SQLite database
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "$BACKUP_DIR/db.sqlite3"
    echo "✅ SQLite database backed up"
else
    echo "⚠️  SQLite database not found"
fi

# Backup media files
if [ -d "media" ] && [ "$(ls -A media)" ]; then
    cp -r media "$BACKUP_DIR/media"
    echo "✅ Media files backed up"
else
    echo "⚠️  No media files to backup"
fi

# Create backup info
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Backup Name: $BACKUP_NAME
Created: $(date)
Type: Quick Backup
Django Project: $(basename $(pwd))
Files:
$(ls -la "$BACKUP_DIR")
EOF

echo "✅ Backup completed: $BACKUP_DIR"
echo ""
echo "📋 To restore this backup later:"
echo "   ./restore_backup.sh $BACKUP_NAME"
echo ""
echo "📋 To manage backups with more features:"
echo "   python backup_manager.py list"
echo "   python backup_manager.py restore $BACKUP_NAME"