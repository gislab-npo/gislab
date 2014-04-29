#
###  DEFAULT WEB PAGE ###
#

# default web server page output
mkdir -p /var/www/default
cat << EOF > /var/www/default/index.html
<html>
<head>
<title>GIS.lab server</title>
</head>
<body bgcolor="white" text="black">
<h1>GIS.lab server</h1>
</body>
</html>
EOF


### APACHE
# change listen port to 8000
cat << EOF > /etc/apache2/ports.conf
$(gislab_config_header)

NameVirtualHost *:8000
Listen 8000

<IfModule mod_ssl.c>
	Listen 443
</IfModule>

<IfModule mod_gnutls.c>
	Listen 443
</IfModule>
EOF

# default virtualhost
cat << EOF > /etc/apache2/sites-available/default
$(gislab_config_header)

<VirtualHost *:8000>
	ServerAdmin root@gis.lab

	DocumentRoot /var/www/default
	<Directory />
		Options FollowSymLinks
		AllowOverride None
	</Directory>
	<Directory /var/www/default/>
		Options -Indexes FollowSymLinks MultiViews
		AllowOverride None
		Order allow,deny
		Allow from all
	</Directory>

	ErrorLog \${APACHE_LOG_DIR}/error.log
	LogLevel warn

	CustomLog \${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF

a2ensite default
service apache2 restart


### NGINX
# proxy parameters
cat << EOF > /etc/nginx/proxy_params
$(gislab_config_header)

proxy_set_header Host \$host;
proxy_set_header X-Real-IP \$remote_addr;
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;

client_max_body_size 100M;
client_body_buffer_size 1m;
proxy_intercept_errors on;
proxy_buffering on;
proxy_buffer_size 128k;
proxy_buffers 256 16k;
proxy_busy_buffers_size 256k;
proxy_temp_file_write_size 256k;
proxy_max_temp_file_size 0;
proxy_read_timeout 300;
EOF

# default virtualhost
cat << EOF > /etc/nginx/sites-available/default
$(gislab_config_header)

server {
        root /var/www/default;
        index index.html index.htm;

        server_name localhost $GISLAB_SERVER_IP boot.gis.lab;

        location / {
                try_files \$uri \$uri/ /index.html;
		}
}
EOF

sudo service nginx restart



# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
