#!/bin/bash
# Vagrant shell provisioner script. DO NOT RUN BY HAND.
# Be careful when adding new provisioning task to create it as
# idempotent operation, which means, that there is no unwanted effect if
# script is called more than once (in case of upgrade).

# Author: Ivan Mincik, ivan.mincik@gmail.com


set -e


# load configuration
source /vagrant/config.cfg
if [ -f /vagrant/config-user.cfg ]
then
	source /vagrant/config-user.cfg
fi

# install and load utility functions
mkdir -p /usr/local/gislab
cp /vagrant/system/functions.sh /usr/local/gislab/
source /usr/local/gislab/functions.sh


# enable installation in debug mode if requested
if [ "$GISLAB_DEBUG_INSTALL" == "yes" ]; then
	set -x
fi


# get provisioning provider name
GISLAB_SERVER_PROVIDER=$1


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
GISLAB_INSTALL_DIR=/tmp/gislab-install-$(date +%s)
mkdir -p ${GISLAB_INSTALL_DIR}
cp -a /vagrant/system/install/* ${GISLAB_INSTALL_DIR}
for f in ${GISLAB_INSTALL_DIR}/*; do
	gislab_print_info "Running installation script '$(basename $f)'"
	source $f
	echo "$(gislab_config_header)" >> /etc/gislab/$(basename $f).done
done
rm -r ${GISLAB_INSTALL_DIR}


# vim: set ts=4 sts=4 sw=4 noet:
