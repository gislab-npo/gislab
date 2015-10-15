#!/bin/sh
#

# load boot variables
for netfile in /var/cache/gislab/net-*.conf ; do
	if [ -f "$netfile" ]; then
		. "$netfile"
	fi
done


# set hostname
hostname_postfix=$(echo $IPV4ADDR | sed 's/.*\.//')

HOSTNAME="c${hostname_postfix}"

echo "$HOSTNAME" > /etc/hostname
hostname -b -F /etc/hostname


# configure /etc/hosts
cat <<EOF >>/etc/hosts
$IPV4DNS0      server.gis.lab	   server
$IPV4ADDR      $HOSTNAME.gis.lab   $HOSTNAME
EOF


# prohibit network-manager from messing with the boot interface
if [ -w "/etc/network/interfaces" ]; then
	if [ -n "$DEVICE" ]; then
		echo ""
		echo "auto $DEVICE"
		echo "iface $DEVICE inet manual"
	fi >> "/etc/network/interfaces" 2>/dev/null || true
fi


# set munin node name
echo "host_name $(hostname)" >> /etc/munin/munin-node.conf


if grep -q 'root=/dev/nbd0' /proc/cmdline; then
	# register pids of nbd-client so that sendsigs doesn't kill
	# them on shutdown/reboot.
	nbd_pids=$(pgrep '^nbd-client')
	for d in /run/sendsigs.omit.d /lib/init/rw/sendsigs.omit.d /var/run/sendsigs.omit.d ; do
		if [ -d "$d" ]; then
			for p in $nbd_pids ; do
				echo "$p" >> "$d"/gislab || true
			done
		fi
	done
fi
