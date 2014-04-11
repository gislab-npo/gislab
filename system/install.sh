#!/bin/bash
# Vagrant shell provisioner script. DO NOT RUN BY HAND.
# Be careful when adding new provisioning task to create it as
# idempotent operation, which means, that there is no unwanted effect if
# script is called more than once (in case of upgrade).

# Author: Ivan Mincik, ivan.mincik@gmail.com


set -e


source /vagrant/config.cfg
if [ -f /vagrant/config-user.cfg ]
then
	source /vagrant/config-user.cfg
fi

if [ "$GISLAB_DEBUG" == "yes" ];
then
	set -x
fi


# get provisioning provider name
GISLAB_SERVER_PROVIDER=$1

# create gislab directory in /etc to store some GIS.lab settings
mkdir -p /etc/gislab

# test if we are running initial installation or performing upgrade
if [ -f "/etc/gislab/installation.done" ]; then
	GISLAB_INSTALLATION_DONE="yes"
else
	GISLAB_INSTALLATION_DONE="no"
fi


GISLAB_INSTALL_DIR=/tmp/gislab-install-$(date +%s)
mkdir -p ${GISLAB_INSTALL_DIR}
cp -a /vagrant/system/install/* ${GISLAB_INSTALL_DIR}
for f in ${GISLAB_INSTALL_DIR}/*; do source $f; done
rm -r ${GISLAB_INSTALL_DIR}


# vim: set ts=4 sts=4 sw=4 noet:
