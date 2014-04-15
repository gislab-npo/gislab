#!/bin/bash

echo "This is an example server plugin."

case $GISLAB_INSTALL_ACTION in
	install)
		echo "Performing initial GIS.lab installation."
		;;
	upgrade)
		echo "Performing GIS.lab upgrade."
		;;
	*)
		echo "Unknown action."
		;;
esac


# vim: set ts=4 sts=4 sw=4 noet:
