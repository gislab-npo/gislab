#!/bin/sh
#

set -e

usage () {
	echo
	echo "This script creates GIS.lab Unit installation ISO image with custom preseed configuration."
	echo
	echo " USAGE: $(basename $0) -s <country code> -t <timezone> [-p <apt proxy server>] -i <ISO image> -w <working directory>"
	echo
	echo "  -s country code (e.g. SK)"
	echo "  -t timezone (e.g. Europe/Bratislava)"
	echo "  -p address of APT proxy server (e.g. http://192.168.1.10:3142) - optional"
	echo "  -i source installation ISO image"
	echo "  -w working directory with enough disk space (two and half time larger then ISO image size)"
	echo
	exit 1
}

clean_up () {
	mount | grep -q " $MOUNT_DIR " && sudo umount $MOUNT_DIR && rm -rf $MOUNT_DIR
	test -d $WORK_DIR && rm -rf $WORK_DIR
}
	

while getopts "s:p:t:i:w:" OPTION; do

	case "$OPTION" in
		s) COUNTRY_CODE="$OPTARG" ;;
		p) APT_PROXY="$OPTARG" ;;
		t) TIMEZONE="$OPTARG" ;;
		i) SRC_IMAGE="$OPTARG" ;;
		w) WORK_DIR="$OPTARG"
		   ROOT_DIR="$WORK_DIR/root" ;;
		\?) usage ;;
	esac
done

if [ $# -ne 10 -a $# -ne 12 ]; then
	usage
fi

if [ $(id -u) -ne 0 ]; then
	echo "This command can only be be run with superuser privileges"
fi

PRESEED_CONF="$(dirname $(readlink -f $0))/gislab-unit.seed.template"
MOUNT_DIR="/tmp/gislab-unit-iso-mnt"

mkdir -p $MOUNT_DIR
mkdir -p $WORK_DIR
mkdir -p $ROOT_DIR

# clean up when something go wrong
trap clean_up SIGHUP SIGINT SIGKILL ERR

sudo mount -o loop $SRC_IMAGE $MOUNT_DIR
rsync -a $MOUNT_DIR/ $ROOT_DIR/
umount $MOUNT_DIR

cd $ROOT_DIR

cp $PRESEED_CONF preseed/gislab-unit.seed
sed -i "s;###COUNTRY_CODE###;$COUNTRY_CODE;" preseed/gislab-unit.seed
sed -i "s;###APT_PROXY###;$APT_PROXY;" preseed/gislab-unit.seed
sed -i "s;###TIMEZONE###;$TIMEZONE;" preseed/gislab-unit.seed

sed -i 's/^timeout.*/timeout 3/' isolinux/isolinux.cfg
sed -i 's/^default.*/default gislab-unit/' isolinux/txt.cfg
sed -i '/^default gislab-unit/a\
label gislab-unit\
  menu label ^Install GIS.lab Unit Server\
  kernel /install/vmlinuz\
  append file=/cdrom/preseed/gislab-unit.seed vga=788 initrd=/install/initrd.gz debian-installer/locale=en_US.UTF-8 console-setup/ask_detect=false keyboard-configuration/layout="English (US)" keyboard-configuration/variant="English (US)" quiet --' isolinux/txt.cfg

cd ..

rm -f isolinux/boot.cat

genisoimage -o ubuntu-preseed.iso -b isolinux/isolinux.bin \
            -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 \
            -boot-info-table -iso-level 2 -r root/

rm -rf $ROOT_DIR

echo
echo "New ISO Image: $WORK_DIR/ubuntu-preseed.iso"
echo
