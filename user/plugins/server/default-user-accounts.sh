#!/bin/bash
# Create default user accounts with password 'lab'


DEFAULT_USER_ACCOUNTS=( lab1 )

case $GISLAB_INSTALL_ACTION in
	install)
		echo "Adding default user accounts."
		for account in "${DEFAULT_USER_ACCOUNTS[@]}"
		do
			gislab-adduser -g User -l GIS.lab -m $account@gis.lab -p lab $account
		done
		;;
esac


# vim: set ts=4 sts=4 sw=4 noet:
