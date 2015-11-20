#!/bin/bash
# GIS.lab user account hook for completing account creation once it is created
# in LDAP database.
#
# USAGE: adduser.sh [GISLAB_USER]

source /etc/gislab_version
source $GISLAB_ROOT/system/functions.sh


### OPTIONS
if [ "$1" != "" ]; then
    GISLAB_USER=$1
fi


### VARIABLES
lds="ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:///"


### SANITY CHECKS
if [ "$($lds "(uid=$GISLAB_USER)")" == "" ]; then
    echo "User '$GISLAB_USER' doesn't exist in LDAP database !"
fi


### MAIN SCRIPT
# HOME DIRECTORY
# create home directory
cp -pR $GISLAB_PATH_SYSTEM/accounts/skel $GISLAB_PATH_HOME/$GISLAB_USER

# copy custom files
rsync -a $GISLAB_PATH_CUSTOM/accounts/files/ $GISLAB_PATH_HOME/$GISLAB_USER

chown -R $GISLAB_USER:gislabusers $GISLAB_PATH_HOME/$GISLAB_USER
chmod 0700 $GISLAB_PATH_HOME/$GISLAB_USER

# process template variables
find $GISLAB_PATH_HOME/$GISLAB_USER \
    -type f \
    -exec sed -i "s/{+ GISLAB_USER +}/$GISLAB_USER/g" "{}" \;

find $GISLAB_PATH_HOME/$GISLAB_USER \
    -type f \
    -exec sed -i "s/{+ GISLAB_USER_GIVEN_NAME +}/$GISLAB_USER_GIVEN_NAME/g" "{}" \;

find $GISLAB_PATH_HOME/$GISLAB_USER \
    -type f \
    -exec sed -i "s/{+ GISLAB_USER_SURNAME +}/$GISLAB_USER_SURNAME/g" "{}" \;

find $GISLAB_PATH_HOME/$GISLAB_USER \
    -type f \
    -exec sed -i "s/{+ GISLAB_USER_EMAIL +}/$GISLAB_USER_EMAIL/g" "{}" \;

find $GISLAB_PATH_HOME/$GISLAB_USER \
    -type f \
    -exec sed -i "s/{+ GISLAB_USER_DESCRIPTION +}/$GISLAB_USER_DESCRIPTION/g" "{}" \;

find $GISLAB_PATH_HOME/$GISLAB_USER \
    -type f \
    -exec sed -i "s/{+ GISLAB_USER_SUPERUSER +}/$GISLAB_USER_SUPERUSER/g" "{}" \;

find $GISLAB_PATH_HOME/$GISLAB_USER \
    -type f \
    -exec sed -i "s/{+ GISLAB_USER_GROUPS +}/$GISLAB_USER_GROUPS/g" "{}" \;

# create ~/.gislab directory
mkdir -p $GISLAB_PATH_HOME/$GISLAB_USER/.gislab
chmod 700 $GISLAB_PATH_HOME/$GISLAB_USER/.gislab
chown $GISLAB_USER:gislabusers $GISLAB_PATH_HOME/$GISLAB_USER/.gislab


# POSTGRESQL
# create PostgreSQL user account
createuser -U postgres --no-superuser --no-createdb --no-createrole $GISLAB_USER
psql -U postgres -c "GRANT gislabusers TO $GISLAB_USER;"
psql -U postgres -d gislab -c "CREATE SCHEMA AUTHORIZATION $GISLAB_USER;"

# add user to the database superusers group if creating superuser account
id $GISLAB_USER | grep gislabadmins &> /dev/null && sudo=yes || sudo=no
if [ "$sudo" == "yes" ]; then
    psql -U postgres -c "GRANT gislabadmins TO $GISLAB_USER;"
fi


# PUBLISH DIRECTORY
# create publish directory
mkdir -p /storage/publish/$GISLAB_USER # NFS directory
chown $GISLAB_USER:www-data /storage/publish/$GISLAB_USER
chmod 750 /storage/publish/$GISLAB_USER


# VPN
# place VPN configuration and certificates to ~/.gislab directory
if [ -d "/etc/openvpn" ]; then
    mkdir -p $GISLAB_PATH_HOME/$GISLAB_USER/.gislab

    tar -C /etc \
        -czf $GISLAB_PATH_HOME/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn.tar.gz \
        --transform s/^openvpn/$GISLAB_UNIQUE_ID-vpn/ \
        openvpn/gislab_vpn_ca.crt \
        openvpn/gislab_vpn_ta.key \
        openvpn/client.conf

    chown \
        $GISLAB_USER:gislabusers \
        $GISLAB_PATH_HOME/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn.tar.gz

    chmod \
        0600 \
        $GISLAB_PATH_HOME/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn.tar.gz
fi


### DONE
echo "$(date +%Y-%m-%d-%H:%M:%S)" > $GISLAB_PATH_HOME/$GISLAB_USER/.gislab/account.done

# vim: set ts=8 sts=4 sw=4 et:
