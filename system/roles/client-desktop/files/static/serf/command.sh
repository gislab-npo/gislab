#!/bin/bash

# Run shell command with root privileges. Return last 512 bytes of response and exit code.

COMMAND=$(cat)
RESPONSE=$(sh -c "$COMMAND" 2>&1)
EXIT=$?

RESPONSE521=$(echo $RESPONSE | tail -c 512)
echo "$RESPONSE521, EXIT CODE: $EXIT"


# vim: set ts=4 sts=4 sw=4 noet:
