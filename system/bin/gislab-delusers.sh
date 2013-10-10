#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com


source /vagrant/config.cfg

echo "I: Removing GIS LAB users accounts"

# remove lab users accounts
for account in "${GISLAB_USER_ACCOUNTS_AUTO[@]}"
do
	deluser --remove-home $account
done


# vim: set ts=4 sts=4 sw=4 noet:
