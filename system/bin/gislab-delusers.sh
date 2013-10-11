#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

set -e

source /vagrant/config.cfg
echo -e "\n[GISLAB]: Removing GIS LAB users accounts ...\n"

# remove lab users accounts
for account in "${GISLAB_USER_ACCOUNTS_AUTO[@]}"
do
	deluser --remove-home $account
done

echo -e "\n[GISLAB]: Done."


# vim: set ts=4 sts=4 sw=4 noet:
