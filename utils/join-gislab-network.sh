#!/bin/bash
# Add IP address from GISLAB_NETWORK range to host machine.


DIR=$(dirname $(readlink -f $0))

source $(dirname $DIR)/config.cfg
source $(dirname $DIR)/config-user.cfg

sudo ip addr add $GISLAB_NETWORK.199/24 dev eth0

# vim: set ts=4 sts=4 sw=4 noet:
