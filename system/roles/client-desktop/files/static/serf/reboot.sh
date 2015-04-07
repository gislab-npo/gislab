#!/bin/bash

# Perform machine reboot if no user session is active.

ADDRESS=$(cat)

# test if IP address is matching, if event is limited only for specified IP address
if [ "$ADDRESS" != "" ]; then
	 ip addr show | grep "inet ${ADDRESS}/" || exit 0
fi


if [ ! -f  "/var/lib/gislab/session.lock" ]; then
	logger --tag serf "Performing system reboot."

	serf leave
	/sbin/reboot
else
	logger --tag serf "Can't reboot machine. User session is still active."
fi


# vim: set ts=4 sts=4 sw=4 noet:
