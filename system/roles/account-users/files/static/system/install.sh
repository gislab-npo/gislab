# GIS.lab client account configuration script


# create main configuration directories first
mkdir /etc/skel/.config


# keyboard layout
mkdir -p /etc/skel/.config/xfce4/panel
cp -a $GISLAB_INSTALL_ACCOUNT_ROOT/keyboard-layout/xkb-plugin-14.rc /etc/skel/.config/xfce4/panel/xkb-plugin-14.rc

# add other keyboard layouts then English (us) if requested
if [ "$GISLAB_CLIENT_KEYBOARDS" != "" ]; then
	layouts="us,$(echo $GISLAB_CLIENT_KEYBOARDS | awk -F ':' '{print $1}')"
	variants=",$(echo $GISLAB_CLIENT_KEYBOARDS | awk -F ':' '{print $2}')"
else
	layouts="us"
	variants=""
fi

sed -i "s/^layouts=/layouts=$layouts/" /etc/skel/.config/xfce4/panel/xkb-plugin-14.rc
sed -i "s/^variants=/variants=$variants/" /etc/skel/.config/xfce4/panel/xkb-plugin-14.rc


# Conky
mkdir -p /etc/skel/.config/autostart
cp $GISLAB_INSTALL_ACCOUNT_ROOT/conky/conkyrc /etc/skel/.conkyrc
cp $GISLAB_INSTALL_ACCOUNT_ROOT/conky/conky.desktop /etc/skel/.config/autostart/conky.desktop


# Pidgin
mkdir -p /etc/skel/.purple
cp -a $GISLAB_INSTALL_ACCOUNT_ROOT/pidgin/*.xml /etc/skel/.purple
#cp $GISLAB_INSTALL_ACCOUNT_ROOT/pidgin/pidgin.desktop /etc/skel/.config/autostart/pidgin.desktop


# PostgreSQL
cp $GISLAB_INSTALL_ACCOUNT_ROOT/pgadmin3/pgadmin3 /etc/skel/.pgadmin3


# QGIS
mkdir -p /etc/skel/.config/QGIS
mkdir -p /etc/skel/.qgis2
cp $GISLAB_INSTALL_ACCOUNT_ROOT/qgis/QGIS2.conf /etc/skel/.config/QGIS/QGIS2.conf
cp -a $GISLAB_INSTALL_ACCOUNT_ROOT/qgis/composer_templates /etc/skel/.qgis2/

if [ "$GISLAB_CLIENT_GIS_DEVELOPMENT_SUPPORT" == "yes" ]; then
	mkdir -p /etc/skel/bin
	cp $GISLAB_INSTALL_ACCOUNT_ROOT/qgis/bin/gislab-dev-* /etc/skel/bin
	chmod 755 /etc/skel/bin/*
fi


# final skeleton owner setting
chown -R root:root /etc/skel


# vim: set ts=4 sts=4 sw=4 noet:
