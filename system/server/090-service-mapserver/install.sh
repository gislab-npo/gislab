#
### MAPSERVER ###
#
# Install and configure OWS server (mapserver).

# Logging: 
#   production: /var/log/apache2/mapserver-access.log /var/log/apache2/mapserver-error.log
#   debug:      /var/log/apache2/mapserver-access.log /var/log/apache2/mapserver-error.log


# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  apache2
  apache2-mpm-worker
  libapache2-mod-fcgid
  qgis-mapserver
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# mapserver virtualhost
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/apache/site-mapserver /etc/apache2/sites-available/mapserver
gislab_config_header_to_file /etc/apache2/sites-available/mapserver

a2enmod rewrite
a2enmod expires
a2ensite mapserver
service apache2 reload


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
