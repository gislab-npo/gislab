#!/bin/bash
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

set -e

source /vagrant/config.cfg
if [ -f /vagrant/config-user.cfg ]
then
	source /vagrant/config-user.cfg
fi

echo -e "\n[GISLAB]: Updating user accounts template ...\n"

rm -rf /etc/skel/.config
mkdir /etc/skel/.config

rm -rf /etc/skel/.local
mkdir /etc/skel/.local

rm -rf /etc/skel/Repository
rm -rf /etc/skel/Share
rm -rf /etc/skel/Barrel

# configure menu
mkdir -p /etc/skel/.config/menus
cp /vagrant/system/desktop-session/menus/xfce-applications.menu /etc/skel/.config/menus/

mkdir -p /etc/skel/.local/share/applications
cp /vagrant/system/desktop-session/menus/*.desktop /etc/skel/.local/share/applications/

mkdir -p /etc/skel/.local/share/desktop-directories
cp /vagrant/system/desktop-session/menus/*.directory /etc/skel/.local/share/desktop-directories/


# configure GIS LAB desktop and panel
mkdir -p /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml
# copy XUBUNTU settings to fix uncomplete session loading (for unknown reason) - seems not required
# after setting CLIENT_ENV="DESKTOP_SESSION=xubuntu" in lts.conf
#cp -a /opt/ltsp/i386/etc/xdg/xdg-xubuntu/xfce4/xfconf/xfce-perchannel-xml/* /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/
cp /vagrant/system/desktop-session/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
cp /vagrant/system/desktop-session/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml

mkdir -p /etc/skel/.config/xfce4/panel
cp -a /vagrant/system/desktop-session/xfce4/panel/* /etc/skel/.config/xfce4/panel


# add shared directory
ln -s /mnt/repository /etc/skel/Repository
ln -s /mnt/share /etc/skel/Share
ln -s /mnt/barrel /etc/skel/Barrel


# PostgreSQL
cp /vagrant/system/postgresql/pgadmin3 /etc/skel/.pgadmin3


# QGIS
mkdir -p /etc/skel/.config/QGIS
cp /vagrant/system/qgis/QGIS2.conf /etc/skel/.config/QGIS/QGIS2.conf


echo -e "\n[GISLAB]: Creating GIS LAB users accounts ...\n"
# create user accounts (password: gislab)
for account in "${GISLAB_USER_ACCOUNTS_AUTO[@]}"
do
	# Linux account
	adduser $account --disabled-login --gecos "GIS LAB user"
	chmod go-rwx /home/$account
	echo "$account:lab" | chpasswd

	# PostgreSQL account
	sudo su - postgres -c "createuser --no-superuser --no-createdb --no-createrole $account"
	sudo su - postgres -c "psql -c \"ALTER ROLE $account WITH PASSWORD 'lab';\""
	sudo su - postgres -c "psql -c \"GRANT labusers TO $account;\""
	sudo su - postgres -c "psql -d gislab -c \"CREATE SCHEMA AUTHORIZATION $account;\""

	# NFS directory
	mkdir -p /storage/share/$account
	chown $account:$account /storage/share/$account
done

echo -e "\n[GISLAB]: Done."


# vim: set ts=4 sts=4 sw=4 noet:
