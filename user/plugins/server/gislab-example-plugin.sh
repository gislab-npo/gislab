#!/bin/bash
# Example GIS.lab server plugin


echo "Running example GIS.lab server plugin."
case $GISLAB_INSTALL_ACTION in
	install)
		echo "Performing initial GIS.lab server installation."
		;;
	upgrade)
		echo "Performing GIS.lab server upgrade."
		;;
	*)
		echo "Unknown action."
		;;
esac

# vim: set ts=4 sts=4 sw=4 noet:
