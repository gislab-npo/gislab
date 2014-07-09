#!/bin/bash
# GIS.lab installation script. DO NOT RUN BY HAND.

# Be careful when modifying this script. Each task must be created as
# idempotent operation, which means that there is no unwanted effect if
# script is called more than once (in case of upgrade).

# Author: Ivan Mincik, ivan.mincik@gmail.com

set -e

# get root directory of GIS.lab installation package
GISLAB_ROOT=/vagrant
export GISLAB_ROOT

# load utility functions
source $GISLAB_ROOT/system/functions.sh

# load configuration
gislab_config


# get provisioning provider name
GISLAB_SERVER_PROVIDER=$1
export GISLAB_SERVER_PROVIDER

# get current time
GISLAB_INSTALL_DATETIME=$(date +"%Y-%m-%d-%T")
export GISLAB_INSTALL_DATETIME

# get server architecture - 32 bit (i386) or 64 bit (x86_64)
GISLAB_SERVER_ARCHITECTURE=$(uname -i)
export GISLAB_SERVER_ARCHITECTURE

# get provisioning user name and ID
GISLAB_PROVISIONING_USER=$(stat -c %U $GISLAB_ROOT/config.cfg)
export GISLAB_PROVISIONING_USER

# Re-read IP from running server and update GISLAB_NETWORK. This is done because some 
# providers (like AWS) are setting this value by their own.
GISLAB_SERVER_IP=$(hostname  -I | awk -F" " '{print $NF}')
GISLAB_NETWORK=$(echo $GISLAB_SERVER_IP | awk -F "." '{ print $1 "." $2 "." $3 }')
export GISLAB_SERVER_IP
export GISLAB_NETWORK

# Distinguish if we are running initial installation or upgrade.
# More granular check could be provided by checking individual touch files (/var/lib/gislab/*.done)
# created for each installation script when finished.
mkdir -p /var/lib/gislab
if [ -f "/var/lib/gislab/installation.done" ]; then
	GISLAB_INSTALL_ACTION="upgrade"
else
	GISLAB_INSTALL_ACTION="install"
fi
export GISLAB_INSTALL_ACTION

# test if all required plugins are available
if [ -n "$GISLAB_PLUGINS_REQUIRE" ]; then
	for plugin in "${GISLAB_PLUGINS_REQUIRE[@]}"; do
		if [ ! -f "$GISLAB_ROOT/user/plugins/$plugin" ]; then
			gislab_print_error "Missing required plugin '$plugin'"
		fi
	done
fi

# override suite value if requested from environment variable (GISLAB_SUITE_OVERRIDE=<value> bash install.sh)
if [ -n "$GISLAB_SUITE_OVERRIDE" ]; then
	GISLAB_SUITE=$GISLAB_SUITE_OVERRIDE
fi
export GISLAB_SUITE

# turn on debug mode if requested
if [ "$GISLAB_DEBUG_INSTALL" == "yes" ]; then
	set -x
fi


# perform installation
GISLAB_INSTALL_CLIENT_ROOT=$GISLAB_ROOT/system/client
export GISLAB_INSTALL_CLIENT_ROOT

for directory in $GISLAB_ROOT/system/server/*; do
	GISLAB_INSTALL_CURRENT_ROOT=$directory
	GISLAB_INSTALL_CURRENT_SERVICE=$(echo $(basename $GISLAB_INSTALL_CURRENT_ROOT) | sed "s/^...-//")
	gislab_print_info "Running installation script '$GISLAB_INSTALL_CURRENT_SERVICE'"
	
	# if exists, load provider installation script rather than default one
	if [ -f "$GISLAB_INSTALL_CURRENT_ROOT/install-$GISLAB_SERVER_PROVIDER.sh" ]; then
		source $GISLAB_INSTALL_CURRENT_ROOT/install-$GISLAB_SERVER_PROVIDER.sh
	else
		source $GISLAB_INSTALL_CURRENT_ROOT/install.sh
	fi

	echo "$(gislab_config_header)" >> /var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done
done


# vim: set ts=4 sts=4 sw=4 noet:
