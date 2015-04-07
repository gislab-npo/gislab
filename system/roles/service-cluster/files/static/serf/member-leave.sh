#!/bin/bash

# Perform actions when a machines leaves or fails out of the GIS.lab cluster.
# Script removes machine from the GIS.lab OWS load balancer cluster (if exists).


while read line; do
	NAME=`echo $line | awk '{print \$1 }'`
	ADDRESS=`echo $line | awk '{print \$2 }'`
	sed -i'' "/server ${ADDRESS} .*Managed by Serf$/d" /etc/haproxy/haproxy.cfg
done

service haproxy reload


# vim: set ts=4 sts=4 sw=4 noet:
