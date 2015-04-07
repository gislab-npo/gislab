#!/bin/bash

# Perform actions when a machine joins the GIS.lab OWS load balancer cluster.
# Script adds machine to the load balancer. Machine is automatically removed when it leaves cluster.


ADDRESS=$(cat)

# sanity checks
# test if IP address format
if [[ ! $ADDRESS =~ ^([0-9]{1,3}[\.]){3}[0-9]{1,3}$ ]]; then
	logger --tag serf "Invalid IP address format when joining to GIS.lab OWS load balancer cluster ($ADDRESS)"
	exit 1
fi

echo -e "    server $ADDRESS $ADDRESS:91 check observe layer7  # Managed by Serf" >> /etc/haproxy/haproxy.cfg

service haproxy reload


# vim: set ts=4 sts=4 sw=4 noet:
