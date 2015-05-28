#!/bin/bash

# Run script located in 'Publish' directory with root privileges. Return last 512 bytes of response and exit code.


SCRIPT_PATH=$(cat) # must begin with username

PUBLISH_PATH=/mnt/publish
SCRIPT=$PUBLISH_PATH/$SCRIPT_PATH


if [ -f "$SCRIPT" ]; then
	RESPONSE=$($SCRIPT 2>&1)
	EXIT=$?

	RESPONSE521=$(echo $RESPONSE | tail -c 512)
	echo "$RESPONSE521, EXIT CODE: $EXIT"
else
	echo "Script '$SCRIPT' not found !, EXIT CODE: 1"
fi


# vim: set ts=4 sts=4 sw=4 noet:
