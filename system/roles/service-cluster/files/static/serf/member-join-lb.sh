#!/bin/bash

# Perform actions when a machine requests to join the GIS.lab OWS load balancer:
#  * activate machine in load balancer. Machine is automatically removed when it leaves cluster.


ADDRESS=$(cat)
HAPROXYCFG="/etc/haproxy/haproxy.cfg"

# sanity checks
# test if IP address format
if [[ ! $ADDRESS =~ ^([0-9]{1,3}[\.]){3}[0-9]{1,3}$ ]]; then
	logger --tag serf "Invalid IP address format when joining to GIS.lab OWS load balancer ($ADDRESS)"
	exit 1
fi


if [ -f "$HAPROXYCFG" ]; then
	echo -e "    server $ADDRESS $ADDRESS:91 check observe layer7  # Managed by Serf" >> $HAPROXYCFG
	service haproxy reload
else
	logger --tag serf "HAProxy configuration not found when joining to GIS.lab OWS load balancer ($ADDRESS)"
fi


# vim: set ts=4 sts=4 sw=4 noet:
