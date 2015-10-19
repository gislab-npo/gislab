#!/bin/bash

# Perform actions when GIS.lab OWS load balancer join event is received:
#  * reload load balancer if installed


HAPROXY=/usr/sbin/haproxy

if [ -f "$HAPROXY" ]; then
	service haproxy reload
fi


# vim: set ts=4 sts=4 sw=4 noet:
