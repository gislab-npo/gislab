#!/bin/bash

# Perform actions when a machines leaves or fails out of the GIS.lab cluster:
#  * remove machine from the GIS.lab OWS load balancer, running 'server' or 'lab' suite


HAPROXYCFG="/etc/haproxy/haproxy.cfg"

while read line; do
	NAME=`echo $line | awk '{print \$1 }'`
	ADDRESS=`echo $line | awk '{print \$2 }'`

	# HAProxy doesn't exist if GISLAB_SUITE=office
	if [ -f "$HAPROXYCFG" ]; then
		sed -i'' "/server ${ADDRESS} .*Managed by Serf$/d" $HAPROXYCFG
	fi
done


# restart HAProxy only if exists
if [ -f "$HAPROXYCFG" ]; then
	service haproxy reload
fi


# vim: set ts=4 sts=4 sw=4 noet:
