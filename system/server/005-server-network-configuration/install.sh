#
### SERVER NETWORK CONFIGURATION ###
#
# Run server network configuration.

# Export current GIS.lab server IP address and network number when upgrading.
if [ -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then
	GISLAB_SERVER_IP=$(hostname  -I | awk -F" " '{print $NF}')
	GISLAB_NETWORK=$(echo $GISLAB_SERVER_IP | awk -F "." '{ print $1 "." $2 "." $3 }')
	export GISLAB_SERVER_IP
	export GISLAB_NETWORK
fi


### DO NOT CONTINUE ON UPGRADE ###
if [ -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then return; fi

export GISLAB_SERVER_IP="$GISLAB_NETWORK.5"
export GISLAB_NETWORK

# get all interfaces
devs="$(ip link | awk '/ eth[0-9]+:/ { gsub(/:/,""); print $2 }')"

# exit if network card was not found
if [ -z "$devs" ]; then
	gislab_print_error "Cannot find any network card."
fi

# set network interfaces up
for dev in $devs; do
	ip link set dev $dev up
done

# give a little time for network interfaces to recognize plugged/unplugged cables
sleep 5

# use last network card with plugged cable as a primary nic
for dev in $devs; do
	if grep -q 1 /sys/class/net/$dev/carrier 2>/dev/null; then
		iface=$dev
	fi
done

# exit if cable is not connected
if [ -z "$iface" ]; then
	gislab_print_error "Network cable not plugged."
fi

# Check whether the primary interface (on running server) is already configured to get
# IP address from DHCP server. If so prevent this nic from reinitializing it later
# during installation (do this because we cannot flush IP address on Amazon instance,
# otherwise we lose connection to it), but only if GISLAB_SERVER_IP='dhcp' (see below).
grep -q "^iface $iface inet dhcp" /etc/network/interfaces && skip_iface_reinit=yes

# Generate network configuration file

# basic network configuration
cat << EOL > /etc/network/interfaces
$(gislab_config_header)

# The loopback network interface
auto lo
iface lo inet loopback

# Virtualbox has configuration for eth0 in separate file.
# Don't matter if this file doesn't exist.
source /etc/network/interfaces.d/*.cfg

# GIS.lab server primary network interface
EOL

# configure primary interface to get IP address from DHCP server...
if [ "$GISLAB_SERVER_LAN_IP" == "dhcp" ]; then
	cat << EOL >> /etc/network/interfaces
auto $iface
iface $iface inet dhcp
EOL

# ... or configure primary interface with static IP address
else
	cat << EOL >> /etc/network/interfaces
auto $iface
iface $iface inet static
	address $GISLAB_SERVER_LAN_IP
	netmask $GISLAB_SERVER_LAN_NETMASK
	network $GISLAB_SERVER_LAN_NETWORK
	broadcast $GISLAB_SERVER_LAN_BROADCAST
	gateway $GISLAB_SERVER_LAN_GATEWAY
EOL
fi

# Add $GISLAB_SERVER_IP to primary interface only when suite is 'lab'
# to avoid exporting wrong IP address of GIS.lab server when runnig
# installation on Amazon instance.
if [ "$GISLAB_SUITE" == "lab" ]; then
	# add into configuration file
	cat << EOL >> /etc/network/interfaces
	up ip addr add $GISLAB_SERVER_IP/24 dev $iface
EOL
	# ... and to the nic but only if it can't be reinitialized
	if [ "$skip_iface_reinit" == "yes" ]; then
		ip addr add $GISLAB_SERVER_IP/24 dev $iface
	fi
fi

# Reinitialize primary network interface with new configuration.
# Wait 5 second before setting primary nic up then delete default gateway.
# This is necessary if there is another nic configured via DHCP (e.g. Virtualbox provider)
# because it takes some time to do that. Otherwise deleting default gateway has no effect.
if [ "$GISLAB_SERVER_LAN_IP" != "dhcp" -o "$skip_iface_reinit" != "yes" ]; then
	cat << EOL >> /etc/network/interfaces
	pre-up sleep 5
	pre-up ip route del default 2>/dev/null || true
EOL
	# finally reinitialize primary interface with new configuration
	ifdown $iface 2>/dev/null || true
	ip addr flush $iface
	ifup $iface
fi

# re-read IP address from running server and update variables
GISLAB_SERVER_IP="$(ip addr show dev $iface | awk '/inet / { print $2 }' | tail -1 | sed 's/\/[0-9]\+$//')"
GISLAB_NETWORK="$(echo $GISLAB_SERVER_IP | sed 's/\.[0-9]\+$//')"
export GISLAB_SERVER_IP
export GISLAB_NETWORK


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
