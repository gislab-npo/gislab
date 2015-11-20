#!/bin/bash
# GIS.lab user account hook for completing account removal once it is dropped
# from LDAP database.
#
# USAGE: deluser.sh [GISLAB_USER]

source /etc/gislab_version
source $GISLAB_ROOT/system/functions.sh


# read GISLAB_USER from script parameter if given
if [ "$1" != "" ]; then
    GISLAB_USER=$1
fi


lds="ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:///"

# sanity check
if [ "$($lds "(uid=$GISLAB_USER)")" != "" ]; then
    echo "User '$GISLAB_USER' still exist in LDAP database !"
    exit 1
fi


### HOME DIRECTORY
# remove home directory
rm -rf $GISLAB_PATH_HOME/$GISLAB_USER


### POSTGRESQL
# drop database schema
psql -U postgres -d gislab -c "DROP SCHEMA $GISLAB_USER CASCADE"
psql -U postgres -d gislab -c "DROP OWNED BY $GISLAB_USER CASCADE"

# delete data from GIS.lab Web client if installed
ball_exist_sql="SELECT 1 FROM information_schema.tables WHERE table_name = 'storage_ball'"
if [[ $(psql -U postgres -d gislab -tAc "$ball_exist_sql") == "1" ]]; then
    psql -U postgres -d gislab \
        -c "DELETE FROM storage_drawing WHERE \"user\" = '$GISLAB_USER'"
    psql -U postgres -d gislab \
        -c "DELETE FROM storage_ball WHERE \"user\" = '$GISLAB_USER'"
fi

# drop database user
dropuser -U postgres $GISLAB_USER


### PUBLISH DIRECTORY
rm -rf /storage/publish/$GISLAB_USER

# vim: set ts=8 sts=4 sw=4 et:
