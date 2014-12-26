#!/bin/bash
# Modify DHCP client in initrd image to ensure that IP address will be taken only
# from correct GIS.lab server

set -e
set -u

source /etc/gislab_version


INITRD_PATH=/opt/ltsp/i386/boot
INITRD=$(readlink $INITRD_PATH/initrd.img)

mkdir -p /var/tmp/initrd
cd /var/tmp/initrd

cp -vf $INITRD_PATH/$INITRD ./$INITRD.gz
gunzip $INITRD.gz
cpio -id < $(ls)

# change 'udhcp' script with our version
cp -vf $GISLAB_INSTALL_CLIENT_ROOT/udhcp/udhcp scripts/init-premount/
chmod 0775 scripts/init-premount/udhcp

rm -vf $INITRD
find . | cpio --create --format='newc' > /var/tmp/$INITRD
gzip /var/tmp/$INITRD
mv -vf /var/tmp/$INITRD.gz /var/lib/tftpboot/ltsp/i386/$INITRD
rm -rf /var/tmp/initrd*


# vim: set ts=4 sts=4 sw=4 noet:
