#!/bin/bash

echo "This is an example account plugin."

case $GISLAB_ACCOUNT_ACTION in
	add)
		echo "Adding user '$GISLAB_USER'."
		;;
	remove)
		echo "Removing user '$GISLAB_USER'."
		;;
	*)
		echo "Unknown action."
		;;
esac


# vim: set ts=4 sts=4 sw=4 noet:
