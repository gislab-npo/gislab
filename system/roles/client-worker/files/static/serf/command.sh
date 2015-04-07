#!/bin/bash

# Run shell command with root privileges.

COMMAND=$(cat)
sh -c "$COMMAND" 2>&1 || true


# vim: set ts=4 sts=4 sw=4 noet:
