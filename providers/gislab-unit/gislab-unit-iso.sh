#!/bin/bash

# Download Ubuntu Server AMD64 image from http://cdimage.ubuntu.com/releases/bionic/release/

set -e


### USAGE
function usage() {
    echo "USAGE: $(basename $0) [OPTIONS]"
    echo "Create GIS.lab base system installation ISO image from Ubuntu Server ISO."
    echo "Script must be executed with superuser privileges."
    echo -e "\nOPTIONS
    -s country code used for choosing closest repository mirror (e.g. SK)
    -t timezone (e.g. Europe/Bratislava)
    -d disk size in GB (recommended options: 60, 120, 240, 480; default: 60)
    -a swap size in GB (default: 4)
    -k SSH public key file, which will be used for GIS.lab installation or update
    -w working directory with enough disk space (2.5 x larger than ISO image size)
    -i Ubuntu Server installation ISO image file
    -h display this help
    "
    exit 255
}


### OPTIONS
while getopts "s:t:d:a:i:w:k:h" OPTION; do
    case "$OPTION" in
        s) COUNTRY_CODE="$OPTARG" ;;
        t) TIME_ZONE="$OPTARG" ;;
        d) DISK_SIZEGB="$OPTARG" ;;
        a) DISK_SIZE_SWAPGB="$OPTARG" ;;
        k) SSH_PUBLIC_KEY="$OPTARG" ;;
        w) WORK_DIR="$OPTARG"
           ROOT_DIR="$WORK_DIR/root" ;;
        i) SRC_IMAGE="$OPTARG" ;;
        h) usage ;;
        \?) usage ;;
    esac
done


### VARIABLES
SRC_DIR="$(dirname $(readlink -f $0))"
MOUNT_DIR="/tmp/gislab-base-system-iso-mnt"
ISO_ID=$(pwgen -n 8 1)
DATE=$(date '+%Y-%m-%d-%H:%M:%S')


### SANITY CHECKS
if [ -z "$COUNTRY_CODE" \
    -o -z "$TIME_ZONE" \
    -o -z "$SRC_IMAGE" \
    -o -z "$WORK_DIR" \
    -o -z "$SSH_PUBLIC_KEY" ]; then
    usage
fi
if [ -z "$DISK_SIZEGB" ]; then
    DISK_SIZEGB=60
fi
if [ -z "$DISK_SIZE_SWAPGB" ]; then
    DISK_SIZE_SWAP=4300
else
    DISK_SIZE_SWAP=${DISK_SIZE_SWAPGB}300
fi

# boot: 530
# root: 27000
# free: 470
DISK_SIZE_STORAGE=$(($DISK_SIZEGB*1000-470-530-27000-$DISK_SIZE_SWAP))
if [ $DISK_SIZE_STORAGE -lt 20000 ]; then
    echo "Invalid disk configuration (storage must be at least the size of 20GB), please check -d and -a flags"
    exit 1
fi

if [ $(id -u) -ne 0 ]; then
    echo "This command can be run only with superuser privileges"
    exit 1
fi

if ! which genisoimage >/dev/null; then
    echo "Cannot find 'genisoimage' binary. Please install appropriate package."
    exit 1
fi


# mount ISO image, check and keep it for rest of the script
mkdir -p $MOUNT_DIR
sudo mount -o loop $SRC_IMAGE $MOUNT_DIR

if [ ! -f "$MOUNT_DIR/install/vmlinuz" ]; then
    echo "Invalid Ubuntu ISO image file. Ubuntu 18.04 Server ISO is required."
    umount $MOUNT_DIR
    exit 1
fi


### FUNCTIONS
clean_up () {
    mount \
        | grep -q " $MOUNT_DIR " \
        && sudo umount $MOUNT_DIR \
        && rm -rf $MOUNT_DIR
    test -d $WORK_DIR && rm -rf $WORK_DIR
}


### MAIN SCRIPT
mkdir -p $WORK_DIR
mkdir -p $ROOT_DIR


# clean up when something go wrong
trap clean_up SIGHUP SIGINT SIGKILL


# copy ISO image content and umount
rsync -a $MOUNT_DIR/ $ROOT_DIR/
umount $MOUNT_DIR

cd $ROOT_DIR


# boot options
sed -i 's/^timeout.*/timeout 50/' $ROOT_DIR/isolinux/isolinux.cfg
cp -f $SRC_DIR/iso/menu.cfg $ROOT_DIR/isolinux/menu.cfg
cp -f $SRC_DIR/iso/txt.cfg $ROOT_DIR/isolinux/txt.cfg
cp -f $SRC_DIR/iso/splash.pcx $ROOT_DIR/isolinux/splash.pcx


# generate preseed file
cp $SRC_DIR/iso/gislab.seed.template $ROOT_DIR/preseed/gislab.seed
sed -i "s;###COUNTRY_CODE###;$COUNTRY_CODE;" $ROOT_DIR/preseed/gislab.seed
sed -i "s;###TIME_ZONE###;$TIME_ZONE;" $ROOT_DIR/preseed/gislab.seed
sed -i "s;###DISK_SIZE_STORAGE###;$DISK_SIZE_STORAGE;" $ROOT_DIR/preseed/gislab.seed
sed -i "s;###DISK_SIZE_SWAP###;$DISK_SIZE_SWAP;" $ROOT_DIR/preseed/gislab.seed

cp $SSH_PUBLIC_KEY $ROOT_DIR/ssh_key.pub

cp $SRC_DIR/iso/configure-apt-proxy.sh $ROOT_DIR/configure-apt-proxy.sh
chmod 0755 $ROOT_DIR/configure-apt-proxy.sh


# change ISO image name
sed -i "s/^#define DISKNAME.*/#define DISKNAME GIS.lab Base System ($ISO_ID)/" $ROOT_DIR/README.diskdefines
echo "GIS.lab Base System ($ISO_ID)" > $ROOT_DIR/.disk/info

rm -f $ROOT_DIR/isolinux/boot.cat

# update md5sum file
rm -f $ROOT_DIR/md5sum.txt
find -type f -print0 \
    | xargs -0 md5sum \
    | grep -v 'isolinux/boot.cat' > $ROOT_DIR/md5sum.txt

cd $WORK_DIR

genisoimage \
    -D -r -V "GIS.lab Base System" \
    -cache-inodes -J -l \
    -b isolinux/isolinux.bin -c isolinux/boot.cat \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -o gislab-base-system-${ISO_ID}.iso root/

# create meta file
cat << EOF >> $WORK_DIR/gislab-base-system-${ISO_ID}.meta
DATE=$DATE
COUNTRY_CODE=$COUNTRY_CODE
TIME_ZONE=$TIME_ZONE
SRC_IMAGE=$(basename $SRC_IMAGE)
SSH_PUBLIC_KEY=$SSH_PUBLIC_KEY
EOF

# cleanup
rm -rf $MOUNT_DIR
rm -rf $ROOT_DIR


### DONE
echo
echo "GIS.lab Base System ISO: $WORK_DIR/gislab-base-system-${ISO_ID}.iso"
echo "GIS.lab Base System ISO meta:  $WORK_DIR/gislab-base-system-${ISO_ID}.meta"
echo

# vim: set ts=8 sts=4 sw=4 et:
