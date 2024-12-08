#!/bin/bash
# MySQL backup script

# Variables
BACKUP_DIR="/home/your/backup/directory"
TIMESTAMP=$(date +"%Y%m%d%H%M")
MYSQL_USER="your mysql user"
MYSQL_PASSWORD="password for your mysql user"
DATABASE_NAME="law_firm"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Backup command
mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD $DATABASE_NAME > "$BACKUP_DIR/${DATABASE_NAME}_$TIMESTAMP.sql"

# Verify success
if [ $? -eq 0 ]; then
    echo "MySQL backup successful: ${DATABASE_NAME}_$TIMESTAMP.sql"
else
    echo "MySQL backup failed!"
fi
