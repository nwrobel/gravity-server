# Script to backup the prod database, to be run daily
# This should be run in a cron job on the prod. server
# 
# Nick Wrobel
# Created: 3/9/16
# Modified: 3/9/16

BACKUP_LOCATION=~/db/daily-prod-backups

DATE=`date +%Y-%m-%d--%H.%M.%S`
FILENAME=$DATE-DB_prod.sql
SQL_CREDENTIALS=~/.mysql/mysql-config
DB_NAME="Gravity_db"

# Create the dump file
mysqldump --defaults-file=$SQL_CREDENTIALS $DB_NAME > $BACKUP_LOCATION/$FILENAME

# Compress using 7zip
# sudo apt-get install p7zip-full
7z a $BACKUP_LOCATION/$FILENAME.7z $BACKUP_LOCATION/$FILENAME
rm $BACKUP_LOCATION/$FILENAME

