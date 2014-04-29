#
### CONNECTION FORWARDING ###
#

# enable IP forwarding for client machines after each server start
cat << EOF > /etc/rc.local
#!/bin/sh -e
$(gislab_config_header)

sysctl -w net.ipv4.ip_forward=1
iptables --table nat --append POSTROUTING --jump MASQUERADE --source $GISLAB_NETWORK.0/24
exit 0
EOF

sh /etc/rc.local


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
