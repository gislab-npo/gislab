#
### MAPSERVER ###
#


# mapserver virtualhost
cp /vagrant/system/server/090-service-mapserver/conf/apache/site-mapserver /etc/apache2/sites-available/mapserver
gislab_config_header_to_file /etc/apache2/sites-available/mapserver

a2enmod rewrite
a2enmod expires
a2ensite mapserver
service apache2 reload


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
