#!/bin/bash

# Perform actions when GIS.lab cluster join event is received:
#  * update statictics system configuration

GISLAB_CLIENTS=$(serf members -tag role=client -status=alive | sed 's/^\(.\+\):.\+$/\1/' | sort -n)

echo "contact.admins.command mail -s \"[GIS.lab ID: gislab_vagrant] \${var:graph_title}\" root

[gis.lab;]

[gis.lab;server]
    address 127.0.0.1
    use_node_name yes
" >/etc/munin/munin.conf

OLD_IFS=$IFS
IFS='
'

for CLIENT in $GISLAB_CLIENTS; do
    HOST=$(echo $CLIENT | awk '{ print $1 }')
    IP=$(echo $CLIENT | awk '{ print $2 }')

    echo "[gis.lab;$HOST.gis.lab]
    address $IP
    use_node_name yes
" >> /etc/munin/munin.conf
done

IFS=$OLD_IFS

# vim: set ts=8 sts=4 sw=4 et:
