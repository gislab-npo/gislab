#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

echo "I: Creating GIS LAB users accounts"

rm -rf /etc/skel/.config
mkdir /etc/skel/.config

rm -rf /etc/skel/.local
mkdir /etc/skel/.local

rm -rf /etc/skel/Share

# configure menu
mkdir -p /etc/skel/.config/menus
cp /vagrant/config/menus/xfce-applications.menu /etc/skel/.config/menus/

mkdir -p /etc/skel/.local/share/applications
cp /vagrant/config/menus/*.desktop /etc/skel/.local/share/applications/

mkdir -p /etc/skel/.local/share/desktop-directories
cp /vagrant/config/menus/*.directory /etc/skel/.local/share/desktop-directories/


# configure GIS LAB desktop and panel
mkdir -p /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml
# copy XUBUNTU settings to fix uncomplete session loading (for unknown reason) - seems not required
# after setting CLIENT_ENV="DESKTOP_SESSION=xubuntu" in lts.conf
#cp -a /opt/ltsp/i386/etc/xdg/xdg-xubuntu/xfce4/xfconf/xfce-perchannel-xml/* /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/
cp /vagrant/config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
cp /vagrant/config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml

mkdir -p /etc/skel/.config/xfce4/panel
cp -a /vagrant/config/xfce4/panel/* /etc/skel/.config/xfce4/panel


# add shared directory
ln -s /mnt/share /etc/skel/Share


# PostgreSQL
cp /vagrant/config/postgresql/pgpass /etc/skel/.pgpass
cp /vagrant/config/postgresql/pgadmin3 /etc/skel/.pgadmin3


# QGIS
mkdir -p /etc/skel/.config/QGIS
cp /vagrant/config/qgis/QGIS2.conf /etc/skel/.config/QGIS/QGIS2.conf


# create 24 user accounts (login: gislab[1-24] password: gislab)
for i in {1..24}
do
	adduser lab$i --disabled-login --gecos "GIS LAB User"
	chmod go-rwx /home/lab$i
	echo "lab$i:lab" | chpasswd
done


# vim: set ts=4 sts=4 sw=4 noet:
