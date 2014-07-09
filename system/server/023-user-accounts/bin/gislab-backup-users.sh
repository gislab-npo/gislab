#!/bin/bash
# Backup all GIS.lab user's accounts.


source $GISLAB_ROOT/system/functions.sh

# require root privileges
gislab_require_root


# backup user accounts
ldapsearch_cmd="ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:///"
for user in $($ldapsearch_cmd -b "ou=People,dc=gis,dc=lab" uid | awk '/^uid: / { print $2 }'); do
	gislab-backupuser $user
done


# vim: set ts=4 sts=4 sw=4 noet:
