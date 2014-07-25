# GIS.lab client installation script
# LTSP troubleshooting https://help.ubuntu.com/community/UbuntuLTSP/ClientTroubleshooting


# backup existing client image
if [ -f /opt/ltsp/images/i386.img ]
then
	gislab_print_info "Creating backup of existing client image and removing expired backups"
	cp /opt/ltsp/images/i386.img /opt/ltsp/images/i386-backup-$GISLAB_INSTALL_DATETIME.img
	find /opt/ltsp/images/ -iname "i386-backup-*.img" -mtime 7 | xargs rm -vf
fi


# create clean copy of client installation scripts
if [ ! -d "/usr/share/ltsp/plugins/ltsp-build-client/Ubuntu.clean" ]; then
	cp -a /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu  /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu.clean
fi

# clean installation scripts
rm -rf /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu
cp -a /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu.clean /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu

# load GIS.lab configuration
cp $GISLAB_ROOT/config.cfg /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/000-gislab-config
if [ -f $GISLAB_ROOT/config-user.cfg ]
then
	cp $GISLAB_ROOT/config-user.cfg /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/001-gislab-config-user
fi

# load custom GIS.lab client installation scripts
cp -av $GISLAB_INSTALL_CLIENT_ROOT/ltsp/* /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/
cp -av $GISLAB_ROOT/user/plugins/client/* /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/


# build client options
# default options
GISLAB_BUILD_CLIENT_OPTS="--arch i386 --purge-chroot --copy-sourceslist --accept-unsigned-packages "

# use APT proxy for client image creation if configured or at least keep downloaded packages on server
if [ -n "${GISLAB_APT_HTTP_PROXY}" ]; then
	GISLAB_BUILD_CLIENT_OPTS+="--http-proxy $GISLAB_APT_HTTP_PROXY "
else
	GISLAB_BUILD_CLIENT_OPTS+="--copy-package-cache "
fi

# install and remove packages
GISLAB_BUILD_CLIENT_OPTS+='--late-packages "$GISLAB_CLIENT_INSTALL_PACKAGES" '
GISLAB_BUILD_CLIENT_OPTS+='--remove-packages "$GISLAB_CLIENT_REMOVE_PACKAGES" '

# enable debug if requested
if [ "$GISLAB_DEBUG_INSTALL" == "yes" ]; then
	GISLAB_BUILD_CLIENT_OPTS+="--debug "
fi

gislab_print_info "Starting client installation"
ltsp-build-client $GISLAB_BUILD_CLIENT_OPTS

ltsp-update-sshkeys
ltsp-update-kernels

# modify DHCP client to be sure that client will always get IP from correct server
PWD_OLD=$(pwd)
INITRD_PATH=/opt/ltsp/i386/boot
INITRD=$(readlink $INITRD_PATH/initrd.img)
GISLAB_SERVER_IP_REGEX=$(hostname -I | awk -F" " '{print $NF}' | sed 's/\./\\\\./g')
mkdir -p /var/tmp/initrd
cd /var/tmp/initrd
cp -vf $INITRD_PATH/$INITRD ./$INITRD.gz
gunzip $INITRD.gz
cpio -id < $(ls)
cp -vf $GISLAB_INSTALL_CLIENT_ROOT/udhcp/udhcp scripts/init-premount/
sed -i "s/###GISLAB_SERVER_IP_REGEX###/$GISLAB_SERVER_IP_REGEX/" scripts/init-premount/udhcp
sed -i "s/###GISLAB_UNIQUE_ID###/$GISLAB_UNIQUE_ID/" scripts/init-premount/udhcp
rm -vf $INITRD
find . | cpio --create --format='newc' > /var/tmp/$INITRD
gzip /var/tmp/$INITRD
mv -vf /var/tmp/$INITRD.gz /var/lib/tftpboot/ltsp/i386/$INITRD
cd $PWD_OLD
rm -rf /var/tmp/initrd*

# GIS.lab client (LTSP) configuration
cat << EOF > /var/lib/tftpboot/ltsp/i386/lts.conf
[default]
LDM_SESSION=/usr/bin/startxfce4
CLIENT_ENV="DESKTOP_SESSION=xubuntu"
HOSTNAME_BASE=c
LDM_THEME=gislab
LTSP_FATCLIENT=True
LOCAL_APPS=False
#SCREEN_02=shell                          # get local root prompt when pressing Ctrl+Alt+F2 
SCREEN_07=ldm
NFS_HOME=/home
FSTAB_1="server:/storage/repository /mnt/repository nfs defaults 0 0"
FSTAB_2="server:/storage/share /mnt/share nfs defaults 0 0"
FSTAB_3="server:/storage/barrel /mnt/barrel nfs defaults 0 0"
FSTAB_4="tmpfs /mnt/temporary tmpfs defaults,noatime,noexec,size=20% 0 0"
EOF

if [ -n "${GISLAB_CLIENT_NETWORK_STORAGE}" ]; then # mount additional shared dir if configured
cat << EOF >> /var/lib/tftpboot/ltsp/i386/lts.conf
FSTAB_4="$GISLAB_CLIENT_NETWORK_STORAGE"
EOF
fi


# PXE boot
# disable plymouth screen for better client troubleshooting on boot
sed -i "s/quiet splash plymouth:force-splash vt.handoff=7//" /var/lib/tftpboot/ltsp/i386/pxelinux.cfg/default


# HTTP boot (alternative method using iPXE)
# To boot via HTTP, client machine must boot iPXE boot image first. This boot image will launch HTTP boot.
# Prepared iPXE boot image exists in 'http-boot/gislab-client-loader.iso.gz' of GIS.lab source code
# or can be created by running '$ make bin/ipxe.iso EMBED=boot-gislab.ipxe' in iPXE source code.

# add boot files (files can be launched by http://boot.gis.lab/<file> or http://$GISLAB_NETWORK.5/<file>)
ln -sf /var/lib/tftpboot/ltsp/i386/vmlinuz /var/www/default/vmlinuz
ln -sf /var/lib/tftpboot/ltsp/i386/initrd.img /var/www/default/initrd.img

# add boot script
cat << EOF > /var/www/default/i386
#!ipxe
kernel http://${GISLAB_NETWORK}.5/vmlinuz ro root=/dev/nbd0 init=/sbin/init-ltsp nbdroot=${GISLAB_NETWORK}.5:ltsp_i386
initrd http://${GISLAB_NETWORK}.5/initrd.img
boot
EOF

service nbd-server restart
service apache2 reload

gislab_print_info "Client installation done"


# vim: set ts=4 sts=4 sw=4 noet:
