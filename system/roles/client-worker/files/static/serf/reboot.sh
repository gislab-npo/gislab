#!/bin/bash

# Perform machine reboot.

ADDRESS=$(cat)

# test if IP address is matching, if event is limited only for specified IP address
if [ "$ADDRESS" != "" ]; then
	 ip addr show | grep "inet ${ADDRESS}/" || exit 0
fi


logger --tag serf "Performing system reboot."

serf leave
/sbin/reboot


# vim: set ts=4 sts=4 sw=4 noet:
