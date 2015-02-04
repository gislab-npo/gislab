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
$ROOTSERVER	server.gis.lab	server
$IPV4ADDR	$HOSTNAME.gis.lab	$HOSTNAME

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF


# prohibit network-manager from messing with the boot interface
if [ -w "/etc/network/interfaces" ]; then
	if [ -n "$DEVICE" ]; then
		echo ""
		echo "auto $DEVICE"
		echo "iface $DEVICE inet manual"
	fi >> "/etc/network/interfaces" 2>/dev/null || true
fi


# remove useless cron jobs
while read job; do
	rm -f "$job"
done <<EOF
/etc/cron.daily/apt
/etc/cron.daily/dpkg
/etc/cron.daily/logrotate
/etc/cron.daily/mlocate
/etc/cron.daily/passwd
/etc/cron.daily/popularity-contest
/etc/cron.daily/standard
/etc/cron.daily/man-db
/etc/cron.weekly/apt-xapian-index
/etc/cron.weekly/man-db
EOF


# set munin node name
echo "host_name $(hostname)" >> /etc/munin/munin-node.conf


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
