#!/bin/bash

set -e

usage () {
	echo
	echo "Create GIS.lab Unit installation ISO image from Ubuntu Server ISO. Script must be executed with superuser"
	echo "privileges."
	echo
	echo "USAGE: $(basename $0) -s <country code> -t <timezone> -k <SSH public key>"
	echo "                          -w <working directory> -i <ISO image>"
	echo
	echo "  -s country code used for choosing closest repository mirror (e.g. SK)"
	echo "  -t timezone (e.g. Europe/Bratislava)"
	echo "  -k SSH public key file, which will be used for GIS.lab installation or update"
	echo "  -w working directory with enough disk space (2.5 x larger free space then ISO image size)"
	echo "  -i Ubuntu Server installation ISO image file"
	echo "  -h this help"
	echo
	exit 1
}

clean_up () {
	mount | grep -q " $MOUNT_DIR " && sudo umount $MOUNT_DIR && rm -rf $MOUNT_DIR
	test -d $WORK_DIR && rm -rf $WORK_DIR
}
	

while getopts "s:t:i:w:k:h" OPTION; do

	case "$OPTION" in
		s) COUNTRY_CODE="$OPTARG" ;;
		t) TIME_ZONE="$OPTARG" ;;
		i) SRC_IMAGE="$OPTARG" ;;
		w) WORK_DIR="$OPTARG"
		   ROOT_DIR="$WORK_DIR/root" ;;
		k) SSH_PUBLIC_KEY="$OPTARG" ;;
		h) usage ;;
		\?) usage ;;
	esac
done


# sanity checks
if [ -z "$COUNTRY_CODE" -o -z "$TIME_ZONE" -o -z "$SRC_IMAGE" -o -z "$WORK_DIR" -o -z "$SSH_PUBLIC_KEY" ]; then
	usage
fi

if [ $(id -u) -ne 0 ]; then
	echo "This command can be run only with superuser privileges"
	exit 1
fi


SRC_DIR="$(dirname $(readlink -f $0))"
MOUNT_DIR="/tmp/gislab-unit-iso-mnt"
ISO_ID=$(pwgen -n 8 1)
DATE=$(date '+%Y-%m-%d-%H:%M:%S')


mkdir -p $MOUNT_DIR
mkdir -p $WORK_DIR
mkdir -p $ROOT_DIR


# clean up when something go wrong
trap clean_up SIGHUP SIGINT SIGKILL


# load original ISO image content
sudo mount -o loop $SRC_IMAGE $MOUNT_DIR

# check if using valid Ubuntu ISO image file
if [ ! -f "$MOUNT_DIR/install/vmlinuz" ]; then
	echo "Invalid Ubuntu ISO image file. Ubuntu 12.04 Server ISO is required."
	umount $MOUNT_DIR
	exit 1
fi

rsync -a $MOUNT_DIR/ $ROOT_DIR/
umount $MOUNT_DIR

cd $ROOT_DIR


# boot options
sed -i 's/^timeout.*/timeout 50/' $ROOT_DIR/isolinux/isolinux.cfg
cp -f $SRC_DIR/preseed/menu.cfg $ROOT_DIR/isolinux/menu.cfg
cp -f $SRC_DIR/preseed/txt.cfg $ROOT_DIR/isolinux/txt.cfg
cp -f $SRC_DIR/preseed/splash.pcx $ROOT_DIR/isolinux/splash.pcx


# generate preseed file
cp $SRC_DIR/preseed/gislab-unit.seed.template $ROOT_DIR/preseed/gislab-unit.seed
sed -i "s;###COUNTRY_CODE###;$COUNTRY_CODE;" $ROOT_DIR/preseed/gislab-unit.seed
sed -i "s;###TIME_ZONE###;$TIME_ZONE;" $ROOT_DIR/preseed/gislab-unit.seed

cp $SSH_PUBLIC_KEY $ROOT_DIR/ssh_key.pub

cp $SRC_DIR/preseed/configure-apt-proxy.sh $ROOT_DIR/configure-apt-proxy.sh
chmod 0755 $ROOT_DIR/configure-apt-proxy.sh


# Change GIS.lab ISO image name
sed -i "s/Ubuntu-Server/GIS.lab $ISO_ID/" $ROOT_DIR/README.diskdefines
sed -i "s/Ubuntu-Server/GIS.lab $ISO_ID/" $ROOT_DIR/.disk/info

rm -f $ROOT_DIR/isolinux/boot.cat

# update md5sum file
rm -f $ROOT_DIR/md5sum.txt
find -type f -print0 | xargs -0 md5sum | grep -v 'isolinux/boot.cat' > $ROOT_DIR/md5sum.txt

cd $WORK_DIR

# create output ISO image file 
#genisoimage -o gislab-unit.iso -b isolinux/isolinux.bin \
#            -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 \
#            -boot-info-table -iso-level 2 -r root/

mkisofs -D -r -V "GIS.lab Unit" -cache-inodes -J -l -b isolinux/isolinux.bin \
	-c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table \
	-o gislab-unit-${ISO_ID}.iso root/

# create meta file
cat << EOF >> $WORK_DIR/gislab-unit-${ISO_ID}.meta
DATE=$DATE
COUNTRY_CODE=$COUNTRY_CODE
APT_PROXY=$APT_PROXY
TIME_ZONE=$TIME_ZONE
SRC_IMAGE=$(basename $SRC_IMAGE)
SSH_PUBLIC_KEY=$SSH_PUBLIC_KEY
EOF

# cleanup
rm -rf $MOUNT_DIR
rm -rf $ROOT_DIR


# done
echo
echo "GIS.lab Unit ISO image: $WORK_DIR/gislab-unit-${ISO_ID}.iso"
echo "GIS.lab Unit ISO meta:  $WORK_DIR/gislab-unit-${ISO_ID}.meta"
echo
