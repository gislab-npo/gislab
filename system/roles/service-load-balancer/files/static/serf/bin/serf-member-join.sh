#!/bin/bash

# The member join script is invoked when a member joins the GIS.lab network.
# Script simply adds the node to the load balancer and statistics monitoring.

# Taken from https://github.com/hashicorp/serf/tree/master/demo/web-load-balancer


while read line; do
	NAME=`echo $line | awk '{print \$1 }'`
	ROLE=`echo $line | awk '{print \$3 }'`
	if [ "x${ROLE}" != "xworker" ]; then
		continue
	fi
	
	# add server to load balancer
	echo $line | \
		awk '{ printf "    server %s %s:91 check observe layer7  # Managed by Serf\n", $1, $2 }' >> /etc/haproxy/haproxy.cfg

	# add server to statistics
	echo $line | \
		awk '{ printf "[gis.lab;%s] # Managed by Serf\n  address %s\n  use_node_name yes\n", $1, $2 }' > /etc/munin/munin-conf.d/$NAME-gislab.conf

done

service haproxy reload
service munin-node restart


# vim: set ts=4 sts=4 sw=4 noet:
