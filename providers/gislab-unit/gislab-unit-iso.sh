#!/bin/bash

set -e

usage () {
	echo
	echo "Create GIS.lab Unit installation ISO image from Ubuntu Server ISO. Script must be executed with superuser"
	echo "privileges."
	echo
	echo "USAGE: $(basename $0) -s <country code> [-p <apt proxy server>] -t <timezone> -i <ISO image>"
	echo "                          -k <SSH public key> -w <working directory>"
	echo
	echo "  -s country code used for choosing closest repository mirror (e.g. SK)"
	echo "  -p APT proxy server (e.g. http://192.168.1.10:3142) [optional]"
	echo "  -t timezone (e.g. Europe/Bratislava)"
	echo "  -i Ubuntu Server installation ISO image file"
	echo "  -k SSH public key file, which will be used for GIS.lab installation or update"
	echo "  -w working directory with enough disk space (2.5 x larger free space then ISO image size)"
	echo "  -h this help"
	echo
	exit 1
}

clean_up () {
	mount | grep -q " $MOUNT_DIR " && sudo umount $MOUNT_DIR && rm -rf $MOUNT_DIR
	test -d $WORK_DIR && rm -rf $WORK_DIR
}
	

while getopts "s:p:t:i:w:k:h" OPTION; do

	case "$OPTION" in
		s) COUNTRY_CODE="$OPTARG" ;;
		p) APT_PROXY="$OPTARG" ;;
		t) TIMEZONE="$OPTARG" ;;
		i) SRC_IMAGE="$OPTARG" ;;
		w) WORK_DIR="$OPTARG"
		   ROOT_DIR="$WORK_DIR/root" ;;
		k) SSH_PUBLIC_KEY="$OPTARG" ;;
		h) usage ;;
		\?) usage ;;
	esac
done


# sanity checks
if [ -z "$COUNTRY_CODE" -o -z "$TIMEZONE" -o -z "$SRC_IMAGE" -o -z "$WORK_DIR" -o -z "$SSH_PUBLIC_KEY" ]; then
	usage
fi

if [ $(id -u) -ne 0 ]; then
	echo "This command can be run only with superuser privileges"
	exit 1
fi


PRESEED_CONF="$(dirname $(readlink -f $0))/preseed/gislab-unit.seed.template"
MOUNT_DIR="/tmp/gislab-unit-iso-mnt"

mkdir -p $MOUNT_DIR
mkdir -p $WORK_DIR
mkdir -p $ROOT_DIR


# clean up when something go wrong
trap clean_up SIGHUP SIGINT SIGKILL


# load original ISO image content
sudo mount -o loop $SRC_IMAGE $MOUNT_DIR
rsync -a $MOUNT_DIR/ $ROOT_DIR/
umount $MOUNT_DIR


# generate preseed file
cd $ROOT_DIR

cp $PRESEED_CONF preseed/gislab-unit.seed
sed -i "s;###COUNTRY_CODE###;$COUNTRY_CODE;" preseed/gislab-unit.seed
sed -i "s;###APT_PROXY###;$APT_PROXY;" preseed/gislab-unit.seed
sed -i "s;###TIMEZONE###;$TIMEZONE;" preseed/gislab-unit.seed

cp $SSH_PUBLIC_KEY $ROOT_DIR/ssh_key.pub
sed -i 's|.*###DUMMY_COMMAND###*.|mkdir /target/home/ubuntu/.ssh; \\\
cp /cdrom/ssh_key.pub /target/home/ubuntu/.ssh/authorized_keys; \\\
chroot /target chown -R ubuntu:ubuntu /home/ubuntu/.ssh; \\\
chroot /target chmod 0700 /home/ubuntu/.ssh; \\\
chroot /target chmod 0600 /home/ubuntu/.ssh/authorized_keys|' preseed/gislab-unit.seed


# boot options
sed -i 's/^timeout.*/timeout 3/' isolinux/isolinux.cfg
sed -i 's/^default.*/default gislab-unit/' isolinux/txt.cfg
sed -i '/^default gislab-unit/a\
label gislab-unit\
  menu label ^Install GIS.lab Server\
  kernel /install/vmlinuz\
  append file=/cdrom/preseed/gislab-unit.seed vga=788 initrd=/install/initrd.gz debian-installer/locale=en_US.UTF-8 console-setup/ask_detect=false keyboard-configuration/layout="English (US)" keyboard-configuration/variant="English (US)" quiet --' isolinux/txt.cfg

cd ..

rm -f isolinux/boot.cat


# create output ISO image file 
#genisoimage -o gislab-unit.iso -b isolinux/isolinux.bin \
#            -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 \
#            -boot-info-table -iso-level 2 -r root/

mkisofs -D -r -V "GIS.lab Unit" -cache-inodes -J -l -b isolinux/isolinux.bin \
	-c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table \
	-o gislab-unit.iso root/

rm -rf $MOUNT_DIR
rm -rf $ROOT_DIR


# done
echo
echo "GIS.lab Unit ISO image: $WORK_DIR/gislab-unit.iso"
echo
