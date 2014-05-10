#!/bin/bash
# Example GIS.lab account hook


echo "This is an example account hook."
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
