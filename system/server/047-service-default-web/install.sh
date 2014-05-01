#
###  DEFAULT WEB PAGE ###
#

# Logging: 
#   production: /var/log/apache2/access.log /var/log/apache2/error.log
#               /var/log/nginx/access.log /var/log/nginx/error.log

#   debug:      /var/log/apache2/access.log /var/log/apache2/error.log
#               /var/log/nginx/access.log /var/log/nginx/error.log


# default web server page output
mkdir -p /var/www/default
cp /vagrant/system/server/047-service-default-web/conf/index.html /var/www/default/index.html


### APACHE
# port 8000 configuration
cp /vagrant/system/server/047-service-default-web/conf/apache/ports.conf /etc/apache2/ports.conf
gislab_config_header_to_file /etc/apache2/ports.conf

# default virtualhost
cp /vagrant/system/server/047-service-default-web/conf/apache/site-default /etc/apache2/sites-available/default
gislab_config_header_to_file /etc/apache2/sites-available/default

a2ensite default
service apache2 restart


### NGINX
# proxy parameters
cp /vagrant/system/server/047-service-default-web/conf/nginx/proxy-parameters /etc/nginx/proxy-parameters
gislab_config_header_to_file /etc/nginx/proxy-parameters

# default virtualhost
cp /vagrant/system/server/047-service-default-web/conf/nginx/site-default /etc/nginx/sites-available/default
gislab_config_header_to_file /etc/nginx/sites-available/default

sudo service nginx restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
