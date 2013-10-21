#!/bin/bash
# Author Ivan Mincik, Gista s.r.o., ivan.mincik@gmail.com

# Mount LTSP server /storage/barrel dir. Requires 'nfs-common' package installed.

set -e

DIR=$( dirname "${BASH_SOURCE[0]}" )

mkdir -p $(dirname $DIR)/mnt/barrel
sudo mount -t nfs4 -o proto=tcp,port=2049 localhost:/storage/barrel $(dirname $DIR)/mnt/barrel

echo -e "\nDone. Umount with: $ sudo umount $(dirname $DIR)/mnt/barrel"

# vim: set ts=4 sts=4 sw=4 noet:
