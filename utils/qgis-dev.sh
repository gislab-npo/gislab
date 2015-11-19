#!/bin/bash
# Run development version of QGIS.

set -e


if [ -f "$HOME/apps/bin/qgis" ]; then
    export LD_LIBRARY_PATH=~/apps/lib/
    ~/apps/bin/qgis
else
    echo "Development version of QGIS is not installed. Run '$ qgis-dev-install' first !"
fi

# vim: set ts=8 sts=4 sw=4 et:
