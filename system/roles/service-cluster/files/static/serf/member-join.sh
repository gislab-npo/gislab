#!/bin/bash

# Perform actions when GIS.lab cluster join event is received:
#  * activate statistics monitoring (it will stay activated even if machine leaves cluster)


while read line; do
	NAME=`echo $line | awk '{print \$1 }'`
	ADDRESS=`echo $line | awk '{print \$2 }'`
	ROLE=`echo $line | awk '{print \$3 }'`

	# do nothing if event was sent by GIS.lab server
	if [ "${ROLE}" == "server" ]; then
		continue
	fi
	
	# activate statistics monitoring
	echo -e "[gis.lab;$NAME] # Managed by Serf\n  address $ADDRESS\n  use_node_name yes\n" > /etc/munin/munin-conf.d/$NAME-gislab.conf

done

service munin-node restart


# vim: set ts=4 sts=4 sw=4 noet:
