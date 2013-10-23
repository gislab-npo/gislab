#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

set -e

source /vagrant/config.cfg
if [ -f /vagrant/config-user.cfg ]
then
	source /vagrant/config-user.cfg
fi

echo -e "\n[gis.lab]: Building client image ...\n"

# add some ltsp-build-client plugins which takes care about our image customizations
rm -vf /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/*gislab*
cp -av /vagrant/system/ltsp/plugins/ltsp-build-client/* /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/

# client image configuration
cat << EOF > /etc/ltsp/ltsp-build-client.conf
GISLAB_VERSION=$GISLAB_VERSION
ARCH=i386
FAT_CLIENT_DESKTOPS="xubuntu-desktop"
LATE_PACKAGES="$GISLAB_CLIENT_INSTALL_PACKAGES"
REMOVE_PACKAGES="
    thunderbird-globalmenu
    abiword
    abiword-common
    abiword-plugin-grammar
    abiword-plugin-mathview
    libabiword-2.9
    gnumeric
    gnumeric-common
    gnumeric-doc
"
EOF

# use APT proxy for client image creation if configured
GISLAB_LTSP_BUILD_CLIENT_OPTS="--purge-chroot --copy-sourceslist --accept-unsigned-packages"
if [ -n "${GISLAB_APT_HTTP_PROXY}" ]; then
	GISLAB_LTSP_BUILD_CLIENT_OPTS="$GISLAB_LTSP_BUILD_CLIENT_OPTS --http-proxy $GISLAB_APT_HTTP_PROXY"
fi
ltsp-build-client $GISLAB_LTSP_BUILD_CLIENT_OPTS

ltsp-update-sshkeys
ltsp-update-kernels

# LTSP configuration
cat << EOF > /var/lib/tftpboot/ltsp/i386/lts.conf
[default]
LDM_SESSION=/usr/bin/startxfce4
CLIENT_ENV="DESKTOP_SESSION=xubuntu"
LDM_THEME=gislab 
LOCAL_APPS=True
SCREEN_02=shell                          # get local root prompt when pressing Ctrl+Alt+F2 
SCREEN_07=ldm
FSTAB_0="server:/home /home nfs defaults 0 0"
FSTAB_1="server:/storage/repository /mnt/repository nfs defaults 0 0"
FSTAB_2="server:/storage/share /mnt/share nfs defaults 0 0"
FSTAB_3="server:/storage/barrel /mnt/barrel nfs defaults 0 0"
EOF

service nbd-server restart

# disable plymouth screen for better client troubleshooting on boot
sed -i "s/quiet splash plymouth:force-splash vt.handoff=7//" /var/lib/tftpboot/ltsp/i386/pxelinux.cfg/default


echo -e "\n[gis.lab]: Done."

# vim: set ts=4 sts=4 sw=4 noet:
