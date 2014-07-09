#
### DHCP SERVER ###
#

# Logging: 
#   production: /var/log/dhcpd-error.log
#   debug:      /var/log/dhcpd-debug.log

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  isc-dhcp-server
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# network interface
cat << EOF > /etc/default/isc-dhcp-server
$(gislab_config_header)
INTERFACES="eth1"
EOF

# DHCP server configuration
cat << EOF > /etc/dhcp/dhcpd.conf
$(gislab_config_header)

log-facility local7;
authoritative;

# custom DHCP option to distinguish more GIS.lab servers in shared LAN
option gislab-unique-id code 224 = text;

subnet $GISLAB_NETWORK.0 netmask 255.255.255.0 {
    option routers $GISLAB_SERVER_IP;

    pool {
        $GISLAB_UNKNOWN_MAC_POLICY unknown clients;
        range $GISLAB_NETWORK.100 $GISLAB_NETWORK.250;
        # return specified DHCP options in offer
        option dhcp-parameter-request-list 1,3,6,14,15,17,51,54,224;
        option domain-name "gis.lab";
        option domain-name-servers $GISLAB_SERVER_IP;
        option broadcast-address $GISLAB_NETWORK.255;
        option subnet-mask 255.255.255.0;
        option root-path "/opt/ltsp/i386";
        option gislab-unique-id "$GISLAB_UNIQUE_ID";
        if substring( option vendor-class-identifier, 0, 9 ) = "PXEClient" {
            filename "/ltsp/i386/pxelinux.0";
        } else {
            filename "/ltsp/i386/nbi.img";
        }
    }
}
EOF


# adding Apparmor profile to enable including of allowed MACs from /etc/dhcp/dhcpd-machines-allowed.conf
cat << EOF > /etc/apparmor.d/local/usr.sbin.dhcpd
$(gislab_config_header)
/etc/dhcp/dhcpd-machines-allowed.conf lrw,
EOF
service apparmor restart

# creating empty MACs file (must always exist)
cat << EOF > /etc/dhcp/dhcpd-machines-allowed.conf
$(gislab_config_header)
group {
}
EOF

# allow MAC addresses if unknown MACs are denied
if [ "$GISLAB_UNKNOWN_MAC_POLICY" == "deny" ];
then
    cat << EOF >> /etc/dhcp/dhcpd.conf
include "/etc/dhcp/dhcpd-machines-allowed.conf";
EOF

	# allow client's MACs
	$GISLAB_ROOT/system/bin/gislab-allowmachines
fi

service isc-dhcp-server restart


### LOGGING ###
if [ "$GISLAB_DEBUG_SERVICES" == "no" ]; then
cat << EOF >> /etc/rsyslog.d/50-default.conf
local7.err /var/log/dhcpd-error.log
EOF
else
cat << EOF >> /etc/rsyslog.d/50-default.conf
local7.* /var/log/dhcpd-debug.log
EOF
fi

# create default log file
touch /var/log/dhcpd-error.log
chmod 0640 /var/log/dhcpd-error.log
chown syslog:adm /var/log/dhcpd-error.log

# check logs with logcheck
echo "/var/log/dhcpd-error.log" >> /etc/logcheck/logcheck.logfiles

service rsyslog restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
