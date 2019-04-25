#!/bin/bash

# Perform actions when GIS.lab OWS load balancer join event is received:
#  * reload load balancer if installed


HAPROXY=/usr/sbin/haproxy

if [ -x "$HAPROXY" ]; then
    systemctl reload haproxy.service
fi

# vim: set ts=8 sts=4 sw=4 et:
