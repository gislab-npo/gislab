#!/bin/bash
# Mount GIS.lab server 'barrel' shared directory. Requires 'nfs-common' package installed and
# running script 'utils/join-gislab-network.sh' first to get connection with server.

set -e

DIR=$(dirname $(readlink -f $0))

source $(dirname $DIR)/config.cfg
source $(dirname $DIR)/config-user.cfg

mkdir -p $(dirname $DIR)/mnt/barrel
sudo mount -t nfs4 -o proto=tcp,port=2049 $GISLAB_NETWORK.5:/storage/barrel $(dirname $DIR)/mnt/barrel

echo -e "\nDone. Umount with: $ sudo umount $(dirname $DIR)/mnt/barrel"

# vim: set ts=4 sts=4 sw=4 noet:
