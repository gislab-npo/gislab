#!/bin/bash

echo "This is an example server plugin."

case $GISLAB_INSTALL_ACTION in
	install)
		echo "We are performing initial GIS.lab installation."
		;;
	upgrade)
		echo "We are performing GIS.lab upgrade."
		;;
	*)
		echo "Unknown."
		;;
esac


# vim: set ts=4 sts=4 sw=4 noet:
