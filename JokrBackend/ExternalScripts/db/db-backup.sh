# This script is used to create a backup of the database
# It takes the filepath to save the backup as an argument
#
# Nick Wrobel
# Created: 3/9/16
# Modified: 3/9/16

SQL_CREDENTIALS=~/.mysql/mysql-config 
DB_NAME="Gravity_db"
FILEPATH=$1

mysqldump --defaults-file=$SQL_CREDENTIALS $DB_NAME > $FILEPATH
 

