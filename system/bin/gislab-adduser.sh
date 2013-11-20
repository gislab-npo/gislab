#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

set -e

# test if account name given as parameter
if [ $# -eq 0 ]
then
	echo "Account name is required!"
	exit 0
fi

# source configuration files
source /vagrant/config.cfg
if [ -f /vagrant/config-user.cfg ]
then
	source /vagrant/config-user.cfg
fi

# /etc/skel update
echo -e "\n[GIS.lab]: Updating user accounts template ..."
rm -rf /etc/skel/.config
mkdir /etc/skel/.config

rm -rf /etc/skel/.local
mkdir /etc/skel/.local

rm -rf /etc/skel/Repository
rm -rf /etc/skel/Share
rm -rf /etc/skel/Barrel


# configure menu
mkdir -p /etc/skel/.config/menus
cp /vagrant/system/client/desktop-session/menus/xfce-applications.menu /etc/skel/.config/menus/

mkdir -p /etc/skel/.local/share/applications
cp /vagrant/system/client/desktop-session/menus/*.desktop /etc/skel/.local/share/applications/

mkdir -p /etc/skel/.local/share/desktop-directories
cp /vagrant/system/client/desktop-session/menus/*.directory /etc/skel/.local/share/desktop-directories/


# configure GIS.lab desktop and panel
mkdir -p /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml
# copy XUBUNTU settings to fix uncomplete session loading (for unknown reason) - seems not required
# after setting CLIENT_ENV="DESKTOP_SESSION=xubuntu" in lts.conf
#cp -a /opt/ltsp/i386/etc/xdg/xdg-xubuntu/xfce4/xfconf/xfce-perchannel-xml/* /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/
cp /vagrant/system/client/desktop-session/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
cp /vagrant/system/client/desktop-session/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml

mkdir -p /etc/skel/.config/xfce4/panel
cp -a /vagrant/system/client/desktop-session/xfce4/panel/* /etc/skel/.config/xfce4/panel


# Conky
mkdir -p /etc/skel/.config/autostart
cp /vagrant/system/client/desktop-session/conky/conkyrc /etc/skel/.conkyrc
cp /vagrant/system/client/desktop-session/conky/conky.desktop /etc/skel/.config/autostart/conky.desktop


# add shared directory
ln -s /mnt/repository /etc/skel/Repository
ln -s /mnt/share /etc/skel/Share
ln -s /mnt/barrel /etc/skel/Barrel


# PostgreSQL
cp /vagrant/system/pgadmin3/pgadmin3 /etc/skel/.pgadmin3


# QGIS
mkdir -p /etc/skel/.config/QGIS
cp /vagrant/system/qgis/QGIS2.conf /etc/skel/.config/QGIS/QGIS2.conf


# create account
echo -e "\n[GIS.lab]: Creating user account ..."
adduser $1 --disabled-login --gecos "GIS.lab user" # Linux account
chmod go-rwx /home/$1
echo "$1:lab" | chpasswd

sudo su - postgres -c "createuser --no-superuser --no-createdb --no-createrole $1" # PostgreSQL account
sudo su - postgres -c "psql -c \"ALTER ROLE $1 WITH PASSWORD 'lab';\""
sudo su - postgres -c "psql -c \"GRANT labusers TO $1;\""
sudo su - postgres -c "psql -d gislab -c \"CREATE SCHEMA AUTHORIZATION $1;\""

mkdir -p /storage/share/$1 # NFS directory
chown $1:$1 /storage/share/$1


echo -e "\n[GIS.lab]: Done."

# vim: set ts=4 sts=4 sw=4 noet:
