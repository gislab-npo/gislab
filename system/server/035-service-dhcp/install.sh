#
### DHCP SERVER ###
#

# adding Apparmor profile to enable including allowed MACs from /etc/ltsp/dhcpd-machines-allowed.conf
cat << EOF > /etc/apparmor.d/local/usr.sbin.dhcpd
$(gislab_config_header)
/etc/ltsp/dhcpd-machines-allowed.conf lrw,
EOF
service apparmor restart

# creating empty MACs file
cat << EOF > /etc/ltsp/dhcpd-machines-allowed.conf
$(gislab_config_header)
group {
}
EOF

# DHCP server configuration
cat << EOF > /etc/ltsp/dhcpd.conf
$(gislab_config_header)
log-facility local7;

authoritative;

subnet $GISLAB_NETWORK.0 netmask 255.255.255.0 {
    option routers $GISLAB_SERVER_IP;

    pool {
        $GISLAB_UNKNOWN_MAC_POLICY unknown clients;
        range $GISLAB_NETWORK.100 $GISLAB_NETWORK.250;
        option domain-name "gis.lab";
        option domain-name-servers $GISLAB_SERVER_IP;
        option broadcast-address $GISLAB_NETWORK.255;
        option subnet-mask 255.255.255.0;
        option root-path "/opt/ltsp/i386";
        if substring( option vendor-class-identifier, 0, 9 ) = "PXEClient" {
            filename "/ltsp/i386/pxelinux.0";
        } else {
            filename "/ltsp/i386/nbi.img";
        }
    }
}
EOF

if [ "$GISLAB_UNKNOWN_MAC_POLICY" == "deny" ]; # if unknown MACs are denied, load known ones from included file
then
    cat << EOF >> /etc/ltsp/dhcpd.conf
include "/etc/ltsp/dhcpd-machines-allowed.conf";
EOF

	# allow client's MACs
	/vagrant/system/bin/gislab-allowmachines
fi

cat << EOF > /etc/default/isc-dhcp-server
$(gislab_config_header)
INTERFACES="eth1"
EOF

# touch log file and set appropriate mode and ownership
touch /var/log/dhcpd-error.log
chmod 0640 /var/log/dhcpd-error.log
chown syslog:adm /var/log/dhcpd-error.log

service isc-dhcp-server restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
