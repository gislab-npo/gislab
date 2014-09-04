#!/bin/bash

# The member leave script is invoked when a member leaves or fails out
# of the GIS.lab network. Script removes the node from the load balancer
# and statistics monitoring.

# Taken from https://github.com/hashicorp/serf/tree/master/demo/web-load-balancer


while read line; do
	NAME=`echo $line | awk '{print \$1 }'`
	sed -i'' "/server ${NAME} .*Managed by Serf$/d" /etc/haproxy/haproxy.cfg
	rm -f /etc/munin/munin-conf.d/$NAME-gislab.conf
done

service haproxy reload


# vim: set ts=4 sts=4 sw=4 noet:
