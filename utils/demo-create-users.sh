#!/bin/bash
# Author: Ivan Mincik, ivan.mincik@gmail.com

set -e

usage(){
	echo "Create multiple GIS.lab user accounts for demonstration purposes."
	echo "All user accounts will be created with password 'lab'."
	echo ""
	echo "USAGE: $0 <number-of-accounts-to-create>"
	exit 0
}

[[ $# -eq 0 ]] && usage


COUNT=$1
for u in $(eval echo "{1..$COUNT}"); do

	gislab-deluser -f lab$u || true
	gislab-adduser -g "User $u" -l "GIS.lab" -m lab$u@gis.lab -p lab lab$u

done


# vim: set ts=4 sts=4 sw=4 noet:
