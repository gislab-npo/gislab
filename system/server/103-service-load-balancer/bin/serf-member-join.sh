#!/bin/bash

# The member join script is invoked when a member joins the GIS.lab network.
# Script simply adds the node to the load balancer

# Taken from https://github.com/hashicorp/serf/tree/master/demo/web-load-balancer


while read line; do
	ROLE=`echo $line | awk '{print \$3 }'`
	if [ "x${ROLE}" != "xworker" ]; then
		continue
	fi
	echo $line | \
		awk '{ printf "    server %s %s:91 check observe layer7  # Managed by Serf\n", $1, $2 }' >> /etc/haproxy/haproxy.cfg
done

/etc/init.d/haproxy reload


# vim: set ts=4 sts=4 sw=4 noet:
