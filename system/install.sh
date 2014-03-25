#!/bin/bash
# Vagrant shell provisioner script. DO NOT RUN BY HAND.
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com


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

GISLAB_INSTALL_DIR=/tmp/gislab-install-$(date +%s)
mkdir -p ${GISLAB_INSTALL_DIR}
cp -a /vagrant/system/install/* ${GISLAB_INSTALL_DIR}

# GISLAB_SUITE="lab"
if [ "$GISLAB_SUITE" == "lab" ]; then
	for f in ${GISLAB_INSTALL_DIR}/*; do source $f; done
fi

# GISLAB_SUITE="server"
if [ "$GISLAB_SUITE" == "server" ]; then
	for f in ${GISLAB_INSTALL_DIR}/*; do
		# exclude client installation
		if [ "$(basename $f)" != "110-client-installation" ]; then
			source $f
		fi
	done
fi

rm -r ${GISLAB_INSTALL_DIR}


# vim: set ts=4 sts=4 sw=4 noet:
