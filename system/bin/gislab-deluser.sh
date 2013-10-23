#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

set -e

# test if account name given as parameter
if [ $# -eq 0 ]
then
	echo "Account name is required!"
	exit 0
fi

# source configuration files
source /vagrant/config.cfg
if [ -f /vagrant/config-user.cfg ]
then
	source /vagrant/config-user.cfg
fi

# remove account
echo -e "\n[gis.lab]: Removing gis.lab user accounts ..."
deluser --remove-home $1 # Linux account

sudo su - postgres -c "psql -d gislab -c \"DROP SCHEMA $1 CASCADE\"" # PostgreSQL account
sudo su - postgres -c "psql -d gislab -c \"DROP OWNED BY $1 CASCADE\""
sudo su - postgres -c "dropuser $1"

rm -rf /storage/share/$1 # NFS directory


echo -e "\n[gis.lab]: Done."

# vim: set ts=4 sts=4 sw=4 noet:
