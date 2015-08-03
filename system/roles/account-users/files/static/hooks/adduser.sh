#!/bin/bash
# GIS.lab user account hook for completing account creation once it is created in LDAP database.
#
# USAGE: adduser.sh <USERNAME>

source /etc/gislab_version


GISLAB_USER=$1

# sanity check
if [ "$(ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:/// "(uid=$GISLAB_USER)")" == "" ]; then
	echo "User '$GISLAB_USER' doesn't exist in LDAP database !"
	exit 1
fi


### HOME DIRECTORY
# create home directory
cp -pR /etc/skel /storage/home/$GISLAB_USER
chown -R $GISLAB_USER:gislabusers /storage/home/$GISLAB_USER
chmod 0700 /storage/home/$GISLAB_USER

# replace user name placeholder with user name of created user
find /storage/home/$GISLAB_USER -type f -exec sed -i "s/{+ GISLAB_USER +}/$GISLAB_USER/g" "{}" \;

# create ~/.gislab directory
mkdir -p /storage/home/$GISLAB_USER/.gislab
chmod 700 /storage/home/$GISLAB_USER/.gislab
chown $GISLAB_USER:gislabusers /storage/home/$GISLAB_USER/.gislab


### POSTGRESQL
# create PostgreSQL user account
createuser -U postgres --no-superuser --no-createdb --no-createrole $GISLAB_USER
psql -U postgres -c "GRANT gislabusers TO $GISLAB_USER;"
psql -U postgres -d gislab -c "CREATE SCHEMA AUTHORIZATION $GISLAB_USER;"

# add user to the database superusers group if creating superuser account
id $GISLAB_USER | grep gislabadmins &> /dev/null && SUDO=yes || SUDO=no
if [ "$SUDO" == "yes" ]; then
	psql -U postgres -c "GRANT gislabadmins TO $GISLAB_USER;"
fi


### PUBLISH DIRECTORY
# create publish directory
mkdir -p /storage/publish/$GISLAB_USER # NFS directory
chown $GISLAB_USER:www-data /storage/publish/$GISLAB_USER
chmod 750 /storage/publish/$GISLAB_USER


### VPN
# place VPN configuration and certificates to ~/.gislab directory
if [ -d "/etc/openvpn" ]; then
	cp /etc/openvpn/gislab_vpn_ca.crt /storage/home/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn_ca.crt
	chown $GISLAB_USER:gislabusers /storage/home/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn_ca.crt

	cp /etc/openvpn/gislab_vpn_ta.key /storage/home/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn_ta.key
	chown $GISLAB_USER:gislabusers /storage/home/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn_ta.key
	chmod 0600 /storage/home/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn_ta.key

	cp /etc/openvpn/client.conf /storage/home/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn.conf
	chown $GISLAB_USER:gislabusers /storage/home/$GISLAB_USER/.gislab/$GISLAB_UNIQUE_ID-vpn.conf
fi


### DONE
echo "$(date +%Y-%m-%d-%H:%M:%S)" > /storage/home/$GISLAB_USER/.gislab/account.done


# vim: set ts=4 sts=4 sw=4 noet:
