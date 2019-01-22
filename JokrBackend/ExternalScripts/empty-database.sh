#!/bin/sh

SQL_CREDENTIALS=/var/webserver/JokrBackend/ExternalScripts/mysql-config
APP_NAME="JokrBackend"
DB_NAME="jokrbackend_db"

# truncate all tables with the app name in the prefix of the table name

mysql --defaults-file=$SQL_CREDENTIALS -Nse \
'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME LIKE "$APP_NAME%";' \
$DB_NAME | while read table; \
do mysql --defaults-file=$SQL_CREDENTIALS \
-e  "SET foreign_key_checks=0; truncate table $table" $DB_NAME; done
