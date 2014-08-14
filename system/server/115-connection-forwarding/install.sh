#
### CONNECTION FORWARDING ###
#
# Activate Internet connection routing from GIS.lab network.


# enable IP forwarding for client machines after each server start
cat << EOF > /etc/init/connection-forwarding.conf
description "Internet connection forwarding"

start on (net-device-up IFACE!=lo)
stop on runlevel [06]

script
iptables --table nat --flush
sysctl -w net.ipv4.ip_forward=1
iptables --table nat --append POSTROUTING --jump MASQUERADE --source $GISLAB_NETWORK.0/24
end script
EOF

service connection-forwarding restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
