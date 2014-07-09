#!/bin/bash
# Backup GIS.lab Web data.


source $GISLAB_ROOT/system/functions.sh

# require root privileges
gislab_require_root

# get current date
DATE=$(date '+%Y-%m-%d:%H-%M-%S')

# backup webgis data
BACKUP_FILE=/storage/backup/gislab-web-balls-backup-$DATE.json

source /usr/local/python-virtualenvs/webgis/bin/activate
/var/www/webgis/manage.py dumpdata storage.Ball > $BACKUP_FILE
gzip $BACKUP_FILE
chmod 400 $BACKUP_FILE.gz


# backup also secrets file
BACKUP_FILE=/storage/backup/gislab-web-settings_secret-$DATE.py
cp /var/www/webgis/djproject/settings_secret.py $BACKUP_FILE
gzip $BACKUP_FILE
chmod 400 $BACKUP_FILE.gz


# vim: set ts=4 sts=4 sw=4 noet:
