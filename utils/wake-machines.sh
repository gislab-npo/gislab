#!/bin/bash
# Wake machines in LAN with given MAC addresses (require etherwake).
# USAGE: $(basename $0) MAC,MAC,...


IFS=', ' read -a maclist <<< "$1"
for mac in "${maclist[@]}"; do
    sudo etherwake -D $mac
done

# vim: set ts=8 sts=4 sw=4 et:
