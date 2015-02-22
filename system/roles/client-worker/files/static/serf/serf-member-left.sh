#!/bin/bash

# The member leave script is invoked when a member leaves or fails out of the GIS.lab network. Script will halt machine.

# Taken from https://github.com/hashicorp/serf/tree/master/demo/web-load-balancer


while read line; do
	ROLE=`echo $line | awk '{print \$3 }'`
	if [ "x${ROLE}" == "xserver" ]; then
		logger -t serf "Received 'left' message from GIS.lab server"
		# poweroff	# poweroff feature was disabled because of problems with random resets of network adapter on GIS.lab
		# Unit hardware, which was causing false 'left' messages.
		# TODO: try to enable 'poweroff' feature after upgrade to Ubuntu 14.04
	fi
done


# vim: set ts=4 sts=4 sw=4 noet:
