#!/bin/bash
# Launch development version of QGIS.

set -e


if [ -f "/home/$USER/apps/bin/qgis" ]; then
	export LD_LIBRARY_PATH=~/apps/lib/
	~/apps/bin/qgis
else
	echo "Development version of QGIS is not installed. Run '$ qgis-dev-install' first !"
fi


# vim: set ts=4 sts=4 sw=4 noet:
