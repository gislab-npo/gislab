#!/bin/bash
# Author Ivan Mincik, Gista s.r.o., ivan.mincik@gmail.com

# Mount LTSP server /storage dir. Requires 'nfs-common' package installed.

mkdir -p storage
sudo mount -t nfs4 -o proto=tcp,port=2049 localhost:/ storage

# vim: set ts=4 sts=4 sw=4 noet:
