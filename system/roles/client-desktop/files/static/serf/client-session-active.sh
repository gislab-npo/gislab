#!/bin/bash

# Return information about currently running user session. 

LOCKFILE="/var/lib/gislab/session.lock"

if [ -f  "$LOCKFILE" ]; then
	echo "yes (user: $(cat $LOCKFILE))"
else
	echo "no"
fi


# vim: set ts=4 sts=4 sw=4 noet:
