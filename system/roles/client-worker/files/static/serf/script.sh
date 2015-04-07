#!/bin/bash

# Run script located in 'Publish' directory with user privileges.

PUBLISH_PATH=/mnt/publish
SCRIPT_PATH=$(cat)
SCRIPT=$PUBLISH_PATH/$SCRIPT_PATH

USERNAME=$(echo $SCRIPT | awk -F '/' '{print $1}')


if [ -f "$SCRIPT" ]; then
	sudo -u $USERNAME sh "$SCRIPT" 2>&1 || true
else
	echo "ERROR: Script '$SCRIPT' not found !"


# vim: set ts=4 sts=4 sw=4 noet:
