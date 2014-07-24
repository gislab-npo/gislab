#
### MAPSERVER ###
#

# Logging: 
#   production: /var/log/apache2/access.log /var/log/apache2/error.log
#   debug:      /var/log/apache2/access.log /var/log/apache2/error.log

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  apache2
  apache2-mpm-worker
  libapache2-mod-fcgid
  qgis-mapserver
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES

sed -i '/^<\/VirtualHost>/d' /etc/apache2/sites-available/default

cat << EOL >> /etc/apache2/sites-available/default

	ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
	<Directory "/usr/lib/cgi-bin">
		AllowOverride All
		Options -Indexes +ExecCGI -MultiViews +SymLinksIfOwnerMatch
		Order allow,deny
		Allow from all

		<files "qgis_mapserv.fcgi">
			RewriteEngine On
			RewriteCond %{QUERY_STRING} ^(.*)map=(.*)(.*) [NC]
			RewriteRule ^(.*)\$ \$1?%1map=/mnt/share/%2%3 [DPI]
		</files>
	</Directory>

#	RewriteLog ${APACHE_LOG_DIR}/error.log
#	RewriteLogLevel 3
</VirtualHost>
EOL

gislab_config_header_to_file /etc/apache2/sites-available/default

a2enmod rewrite
a2enmod expires
service apache2 reload


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
