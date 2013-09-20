#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com


rm -rf /etc/skel/.config
mkdir /etc/skel/.config

rm -rf /etc/skel/.local
mkdir /etc/skel/.local

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
