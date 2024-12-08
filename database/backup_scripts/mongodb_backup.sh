#!/bin/bash
# MongoDB backup script

# Variables
BACKUP_DIR="/home/your/backup/directory"
TIMESTAMP=$(date +"%Y%m%d%H%M")
MONGO_URI="mongodb://localhost:27017"
DATABASE_NAME="your_database_name"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Backup command
mongodump --uri=$MONGO_URI --db=$DATABASE_NAME --out="$BACKUP_DIR/${DATABASE_NAME}_$TIMESTAMP"

# Verify success
if [ $? -eq 0 ]; then
    echo "MongoDB backup successful: ${DATABASE_NAME}_$TIMESTAMP"
else
    echo "MongoDB backup failed!"
fi

