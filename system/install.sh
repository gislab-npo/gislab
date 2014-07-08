#!/bin/bash
# GIS.lab installation script. DO NOT RUN BY HAND.

# Be careful when modifying this script. Each task must be created as
# idempotent operation, which means, that there is no unwanted effect if
# script is called more than once (in case of upgrade).

# Author: Ivan Mincik, ivan.mincik@gmail.com


set -e


# load utility functions
source /vagrant/system/functions.sh

# load configuration
gislab_config


# enable installation in debug mode if requested
if [ "$GISLAB_DEBUG_INSTALL" == "yes" ]; then
	set -x
fi


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
GISLAB_PROVISIONING_USER=$(stat -c %U /vagrant/config.cfg)
export GISLAB_PROVISIONING_USER


# test if all required plugins are available
if [ -n "$GISLAB_PLUGINS_REQUIRE" ]; then
	for plugin in "${GISLAB_PLUGINS_REQUIRE[@]}"; do
		if [ ! -f "/vagrant/user/plugins/$plugin" ]; then
			gislab_print_error "Missing required plugin '$plugin'"
		fi
	done
fi


# create gislab directory in /etc to store some GIS.lab settings
mkdir -p /etc/gislab

# Set variable to distinguish if we are running initial installation or upgrade. It can be used
# by installation scripts or by server plugins.
# More granular check could be provided by checking individual touch files (.done) created for each
# installation script when finished.
if [ -f "/etc/gislab/installation.done" ]; then
	GISLAB_INSTALL_ACTION="upgrade"
else
	GISLAB_INSTALL_ACTION="install"
fi


# override suite value if requested from environment variable (GISLAB_SUITE_OVERRIDE=<value> bash install.sh)
if [ -n "$GISLAB_SUITE_OVERRIDE" ]; then
	GISLAB_SUITE=$GISLAB_SUITE_OVERRIDE
fi


#
# INSTALLATION
#
GISLAB_INSTALL_ROOT=/tmp/gislab-install-$(date +%s)
export GISLAB_INSTALL_ROOT

GISLAB_INSTALL_CLIENT_ROOT=$GISLAB_INSTALL_ROOT/system/client
export GISLAB_INSTALL_CLIENT_ROOT

mkdir -p $GISLAB_INSTALL_ROOT
cp -a /vagrant/* $GISLAB_INSTALL_ROOT

for directory in $GISLAB_INSTALL_ROOT/system/server/*; do
	GISLAB_INSTALL_CURRENT_ROOT=$directory
	GISLAB_INSTALL_CURRENT_SERVICE=$(echo $(basename $GISLAB_INSTALL_CURRENT_ROOT) | sed "s/^...-//")
	gislab_print_info "Running installation script '$GISLAB_INSTALL_CURRENT_SERVICE'"
	source $GISLAB_INSTALL_CURRENT_ROOT/install.sh
	echo "$(gislab_config_header)" >> /etc/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done
done

rm -r $GISLAB_INSTALL_ROOT


# vim: set ts=4 sts=4 sw=4 noet:
