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

    # test if no active user session is running
    if [ ! -f  "/var/lib/gislab/session.lock" ]; then
        logger --tag serf "Performing system $event."

        serf leave
        /sbin/$event
    else
        logger --tag serf "Can't $event machine. User session is still active."
    fi
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

# vim: set ts=8 sts=4 sw=4 et:
