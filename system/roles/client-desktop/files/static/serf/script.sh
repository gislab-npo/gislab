#!/bin/bash

# Run script located in 'Publish' directory with user privileges. Return last 512 bytes of response and exit code.

PUBLISH_PATH=/mnt/publish
SCRIPT_PATH=$(cat)
SCRIPT=$PUBLISH_PATH/$SCRIPT_PATH

USERNAME=$(echo $SCRIPT_PATH | awk -F '/' '{print $1}')


if [ -f "$SCRIPT" ]; then
	RESPONSE=$(sudo -iu $USERNAME $SCRIPT 2>&1)
	EXIT=$?

	RESPONSE521=$(echo $RESPONSE | tail -c 512)
	echo "$RESPONSE521, USERNAME: $USERNAME, EXIT CODE: $EXIT"
else
	echo "Script '$SCRIPT' not found !, EXIT CODE: 1"
fi


# vim: set ts=4 sts=4 sw=4 noet:
