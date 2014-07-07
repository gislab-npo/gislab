#
###  DEFAULT WEB PAGE ###
#

# Logging: 
#   production: /var/log/apache2/access.log /var/log/apache2/error.log
#               /var/log/nginx/access.log /var/log/nginx/error.log

#   debug:      /var/log/apache2/access.log /var/log/apache2/error.log
#               /var/log/nginx/access.log /var/log/nginx/error.log

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  apache2
  apache2-mpm-worker
  nginx
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# default web server page output
mkdir -p /var/www/default
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/index.html /var/www/default/index.html


### APACHE
# port 8000 configuration
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/apache/ports.conf /etc/apache2/ports.conf
gislab_config_header_to_file /etc/apache2/ports.conf

# default virtualhost
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/apache/site-default /etc/apache2/sites-available/default
gislab_config_header_to_file /etc/apache2/sites-available/default

a2ensite default
service apache2 restart


### NGINX
# proxy parameters
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/nginx/proxy-parameters /etc/nginx/proxy-parameters
gislab_config_header_to_file /etc/nginx/proxy-parameters

# default virtualhost
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/nginx/site-default /etc/nginx/sites-available/default
gislab_config_header_to_file /etc/nginx/sites-available/default

sudo service nginx restart


### LOGGING ###
# check logs with logcheck
echo "/var/log/apache2/error.log" >> /etc/logcheck/logcheck.logfiles
echo "/var/log/nginx/error.log" >> /etc/logcheck/logcheck.logfiles


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
