#!/bin/bash

# The member leave script is invoked when a member leaves or fails out
# of the GIS.lab network. Script removes the node from the load balancer.

# Taken from https://github.com/hashicorp/serf/tree/master/demo/web-load-balancer


while read line; do
	NAME=`echo $line | awk '{print \$1 }'`
	sed -i'' "/${NAME} /d" /etc/haproxy/haproxy.cfg
done

/etc/init.d/haproxy reload


# vim: set ts=4 sts=4 sw=4 noet:
