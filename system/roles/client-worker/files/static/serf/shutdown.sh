#!/bin/bash

# Perform machine shutdown or reboot if no user session is active.


HOSTNAMES=$(cat)

perform_event() {
	# detect event type from script file name
	if [ "$(basename $0)" == "shutdown.sh" ]; then
		event="poweroff"
	else
		event="reboot"
	fi

	serf leave
	/sbin/$event
}


if [ "$HOSTNAMES" != "" ]; then
	IFS=', ' read -a HOSTNAMESLIST <<< "$HOSTNAMES"

	# test if hostname is matching, if event is limited only for specified one
	for host in "${HOSTNAMESLIST[@]}"; do
		if [ "$host" == "$(hostname --short)" ]; then
			perform_event
		fi
	done

else
	perform_event
fi


# vim: set ts=4 sts=4 sw=4 noet:
