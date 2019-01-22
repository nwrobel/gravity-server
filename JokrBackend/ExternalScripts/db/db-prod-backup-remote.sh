# Script to back up the production server database remotely from the
# development server.
# Makes a database image on the prod server and copies it to
# our dev server using ftp.
# Uses the db-backup.sh script.
#
# Nick Wrobel
# Created: 3/9/16
# Modified: 3/9/16

# where to store the backup on prod server
BACKUP_LOCATION_REMOTE=~/db

# where to store the backup on our local server
BACKUP_LOCATION_LOCAL=/media/sf_vm_shared/db/prod-backups

DATE=`date +%Y-%m-%d--%H.%M.%S`
FILENAME=$DATE-DB_prod.sql
FILEPATH=$BACKUP_LOCATION/$FILENAME

# SSH into the prod server and execute our backup script from SSH session.
# Pass in the filename to save the backup as
ssh -i ~/.ssh/aws/nick nick@gravitybackend.ddns.net 'bash -s' \
  < db-backup.sh $BACKUP_LOCATION_REMOTE/$FILENAME;

# SFTP and grab the backup file
FTP_CMD="get $BACKUP_LOCATION_REMOTE/$FILENAME $BACKUP_LOCATION_LOCAL"

echo $FTP_CMD
sftp -i ~/.ssh/aws/nick -b /dev/stdin nick@gravitybackend.ddns.net << EOF
get $BACKUP_LOCATION_REMOTE/$FILENAME $BACKUP_LOCATION_LOCAL
EOF





