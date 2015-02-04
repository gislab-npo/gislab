#!/bin/bash

# The member leave script is invoked when a member leaves or fails out
# of the GIS.lab network. Script will halt server.

# Taken from https://github.com/hashicorp/serf/tree/master/demo/web-load-balancer


while read line; do
	ROLE=`echo $line | awk '{print \$3 }'`
	if [ "x${ROLE}" == "xserver" ]; then
		poweroff
	fi
done


# vim: set ts=4 sts=4 sw=4 noet:
