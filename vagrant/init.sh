#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

# LTSP troubleshooting https://help.ubuntu.com/community/UbuntuLTSP/ClientTroubleshooting

set -e


GISLAB_VERSION=0.1~dev

#
### SERVER UPGRADE ###
#
export DEBIAN_FRONTEND=noninteractive

# hold kernel packages from upgrade to avoid a need to restart server after
# installation (Vagrant box could provide up-to-date kernel image)
echo "linux-image-$(uname -r) hold" | dpkg --set-selections
echo "linux-generic-pae hold" | dpkg --set-selections
echo "linux-image-generic-pae hold" | dpkg --set-selections

echo "grub-pc hold" | dpkg --set-selections # hold also grub because some issue

# add APT proxy if available
#cat << EOF > /etc/apt/apt.conf.d/02proxy
#Acquire::http { Proxy "http://<URL>:3142"; };
#EOF

apt-get update
apt-get --assume-yes upgrade
apt-get --assume-yes install ltsp-server-standalone openssh-server isc-dhcp-server tftpd-hpa --no-install-recommends




#
### DHCP ###
#
# TODO: set some more suitable network range
cat << EOF > /etc/ltsp/dhcpd.conf
authoritative;

subnet 192.168.1.0 netmask 255.255.255.0 {
	range 192.168.1.200 192.168.1.250;
    option domain-name "osgis-lab.lan";
    option domain-name-servers 192.168.1.1, 8.8.8.8;
    option broadcast-address 192.168.1.255;
    option routers 192.168.1.1;
    option subnet-mask 255.255.255.0;
    option root-path "/opt/ltsp/i386";
    if substring( option vendor-class-identifier, 0, 9 ) = "PXEClient" {
        filename "/ltsp/i386/pxelinux.0";
    } else {
        filename "/ltsp/i386/nbi.img";
    }
}
EOF

cat << EOF > /etc/default/isc-dhcp-server
INTERFACES="eth1"
EOF

service isc-dhcp-server restart




#
### LTSP ###
#
# LTSP installation
cat << EOF > /etc/ltsp/ltsp-build-client.conf
ARCH=i386
FAT_CLIENT_DESKTOPS="xubuntu-desktop"
LATE_PACKAGES="
	vim
	htop
	mc
"
EOF

ltsp-build-client --arch i386 # TODO: use --mirror http://<URL>:3142/sk.archive.ubuntu.com/ubuntu
ltsp-update-sshkeys
ltsp-update-kernels

# LTSP image configuration
echo -e "VERSION: $GISLAB_VERSION\nBUILD: $(date) ($USER)" > /opt/ltsp/i386/etc/gislab_version

# we must load XUBUNTU session with custom script because LightDM apparently has some problems to load
# it correctly in LTSP environment
cat << EOF > /var/lib/tftpboot/ltsp/i386/lts.conf
[default]
LDM_SESSION=/usr/bin/startxubuntu
LOCAL_APPS=True
LOCAL_APPS_EXTRAMOUNTS=/vagrant/share
SCREEN_02=shell					# get local root prompt when pressing Ctrl+Alt+F2 
SCREEN_07=ldm
EOF

# disable plymouth screen for better client troubleshooting on boot
# sed -i "s/quiet splash plymouth:force-splash vt.handoff=7//" /var/lib/tftpboot/ltsp/i386/pxelinux.cfg/default

# this script sets necessary XUBUNTU session variables and starts XFCE session
cat << EOF > /opt/ltsp/i386/usr/bin/startxubuntu
#!/bin/bash

export DEFAULTS_PATH=/usr/share/gconf/xubuntu.default.path
export MANDATORY_PATH=/usr/share/gconf/xubuntu.mandatory.path
export GDMSESSION=xubuntu

export DESKTOP_SESSION=xubuntu
export XDG_CONFIG_DIRS=/etc/xdg/xdg-xubuntu:/etc/xdg:/etc/xdg
export XDG_DATA_DIRS=/usr/share/xubuntu:/usr/local/share/:/usr/share/:/usr/share

exec /usr/bin/startxfce4
EOF
chmod +x /opt/ltsp/i386/usr/bin/startxubuntu

cp /vagrant/config/xfce4/greybird/*.* /opt/ltsp/i386/usr/share/themes/Greybird/xfwm4/ # fix Greybird windows resizing problem

# add desktop wallpaper
cp /vagrant/config/gislab-wallpaper.png /opt/ltsp/i386/usr/share/xfce4/backdrops

# install extra packages
export LTSP_HANDLE_DAEMONS=false
mount --bind /dev /opt/ltsp/i386/dev
ltsp-chroot
mount -t proc proc /proc

apt-add-repository --yes ppa:imincik/gis && apt-get update # adding my GIS stack PPA

apt-get --assume-yes install rst2pdf
apt-get --assume-yes install libreoffice libreoffice-gtk libreoffice-calc libreoffice-writer gimp flashplugin-installer # office packages
apt-get --assume-yes remove thunderbird-globalmenu abiword abiword-common abiword-plugin-grammar abiword-plugin-mathview \
	libabiword-2.9 gnumeric gnumeric-common gnumeric-doc

apt-get --assume-yes install postgresql postgis postgresql-9.1-postgis pgadmin3 qgis python-qgis qgis-plugin-grass grass \ # GIS user packages
	gdal-bin libgdal1h python-gdal sqlite3 spatialite-bin spatialite-gui

apt-get --assume-yes install git vim-gnome ipython # GIS developer packages

exit
umount /opt/ltsp/i386/proc
umount /opt/ltsp/i386/dev

# finally update image
ltsp-update-image --arch i386
service nbd-server restart




#
### USERS ###
#
mkdir /etc/skel/.config

mkdir -p /etc/skel/.config/menus
cp /vagrant/config/menus/xfce-applications.menu /etc/skel/.config/menus/

mkdir -p /etc/skel/.local/share/applications
cp /vagrant/config/menus/*.desktop /etc/skel/.local/share/applications/

mkdir -p /etc/skel/.local/share/desktop-directories
cp /vagrant/config/menus/*.directory /etc/skel/.local/share/desktop-directories/

mkdir -p /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml
cp -a /opt/ltsp/i386/etc/xdg/xdg-xubuntu/xfce4/xfconf/xfce-perchannel-xml/* /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/

cp /vagrant/config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
cp /vagrant/config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml

mkdir -p /etc/skel/.config/xfce4/panel
cp -a /vagrant/config/xfce4/panel/* /etc/skel/.config/xfce4/panel

# symlink shared directory
chmod +rwx /vagrant/share
sudo ln -s /vagrant/share /etc/skel/Share

# create 24 lab user accounts (login: gislab[1-24] password: gislab)
for i in {1..24}
do
	adduser gislab$i --disabled-login --gecos "GIS LAB User"
	echo "gislab$i:gislab" | chpasswd
done

# vim: set ts=4 sts=4 sw=4 noet:
