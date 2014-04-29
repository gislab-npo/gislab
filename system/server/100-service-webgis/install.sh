#
### GIS.LAB WEB ###
#

# create database and user only on initial installation
if [ ! -f "/etc/gislab/100-service-webgis.done" ]; then
	WEBGIS_DB_PASSWORD=$(pwgen -1 -n 8)
	sudo su - postgres -c "createdb -E UTF8 -T template0 webgis"
	sudo su - postgres -c "createuser --no-superuser --no-createdb --no-createrole webgis" # PostgreSQL account
	sudo su - postgres -c "psql -c \"ALTER ROLE webgis WITH PASSWORD '${WEBGIS_DB_PASSWORD}';\""
fi


# create and activate Python virtualenv
mkdir -p /usr/local/python-virtualenvs
rm -rf /usr/local/python-virtualenvs/webgis
virtualenv --clear --system-site-packages /usr/local/python-virtualenvs/webgis
source /usr/local/python-virtualenvs/webgis/bin/activate


# install requirements and webgis itself
GISLAB_INSTALL_WEBGIS_DIR=/tmp/gislab-install-webgis-$(date +%s)
cp -a /vagrant/system/server/100-service-webgis/app/gislab-web $GISLAB_INSTALL_WEBGIS_DIR
pip install --download-cache=/var/cache/pip --requirement=$GISLAB_INSTALL_WEBGIS_DIR/requirements.txt
pip install gunicorn
python $GISLAB_INSTALL_WEBGIS_DIR/setup.py install > /dev/null
rm -r $GISLAB_INSTALL_WEBGIS_DIR


# install webgis
rm -rf /var/www/webgis
mkdir -p /var/www/webgis
django-admin.py startproject --template=/vagrant/system/server/100-service-webgis/app/gislab-web/webgis/conf/project_template/ djproject /var/www/webgis


if [ ! -f "/etc/gislab/100-service-webgis.done" ]; then
	cat << EOF >> /var/www/webgis/djproject/settings_secret.py
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'webgis',
		'USER': 'webgis',
		'PASSWORD': '$WEBGIS_DB_PASSWORD',
		'HOST': '',
		'PORT': '',
	}
}
EOF
	# create backup of secrets file. It will be used on upgrade
	cp /var/www/webgis/djproject/settings_secret.py /etc/gislab/webgis-settings_secret.py
else
	# on upgrade load secrets file from backup
	cp /etc/gislab/webgis-settings_secret.py /var/www/webgis/djproject/settings_secret.py
fi

# add web alias if configured
if [ -n "$GISLAB_WEB_ALIAS" ]; then
	sed -i "/ALLOWED_HOSTS/aALLOWED_HOSTS += ['$GISLAB_WEB_ALIAS']" /var/www/webgis/djproject/settings.py
fi

python /var/www/webgis/manage.py syncdb --noinput
python /var/www/webgis/manage.py collectstatic --noinput > /dev/null
deactivate


# web server
cat << EOF > /etc/nginx/sites-available/webgis
$(gislab_config_header)

upstream webgis {
	server unix:/var/www/webgis/gunicorn.sock fail_timeout=0;
}
 
server {
	listen 80;
	server_name web.gis.lab;
	client_max_body_size 4G;
 
	access_log /var/log/nginx/webgis-access.log;
	error_log /var/log/nginx/webgis-error.log;
	
	location /static/ {
		alias /var/www/webgis/static/;
	}

	location /media/ {
		alias /var/www/webgis/media/;
	}
 
	location / {
		include /etc/nginx/proxy_params;
		proxy_redirect off;

		if (!-f \$request_filename) {
			proxy_pass http://webgis;
			break;
		}
	}
 
	error_page 500 502 503 504 /500.html;
	location = /500.html {
		root /var/www/webgis/static/;
	}
}
EOF

ln -sf /etc/nginx/sites-available/webgis /etc/nginx/sites-enabled/webgis

# add web alias if configured
if [ -n "$GISLAB_WEB_ALIAS" ]; then
	sed -i "s/server_name web.gis.lab;/server_name web.gis.lab $GISLAB_WEB_ALIAS;/" /etc/nginx/sites-available/webgis
fi


# Gunicorn deployment
# get number of CPU for setting Gunicorn workers
cpus=$(cat /proc/cpuinfo  | grep processor | wc -l)

if [ $cpus > 1 ]; then
	gunicorn_workers=$(echo $cpus*2 + 1 | bc)
else
	gunicorn_workers=3
fi

# Gunicorn startup script
cat << EOF > /var/www/webgis/gunicorn.sh
#!/bin/bash
$(gislab_config_header)

NAME="webgis"
DJANGODIR=/var/www/webgis
SOCKFILE=/var/www/webgis/gunicorn.sock
USER=www-data
GROUP=www-data
NUM_WORKERS=$gunicorn_workers
DJANGO_SETTINGS_MODULE=djproject.settings
DJANGO_WSGI_MODULE=djproject.wsgi
 
cd \$DJANGODIR
source /usr/local/python-virtualenvs/webgis/bin/activate
export DJANGO_SETTINGS_MODULE=\$DJANGO_SETTINGS_MODULE
export PYTHONPATH=\$DJANGODIR:\$PYTHONPATH
 
RUNDIR=\$(dirname \$SOCKFILE)
test -d \$RUNDIR || mkdir -p \$RUNDIR
 
exec gunicorn \${DJANGO_WSGI_MODULE}:application \
--name \$NAME \
--workers \$NUM_WORKERS \
--user=\$USER --group=\$GROUP \
--log-level=debug \
--bind=unix:\$SOCKFILE
EOF

# Gunicorn Upstart script
cat << EOF > /etc/init/webgis.conf
$(gislab_config_header)

description "GIS.lab Web"
start on runlevel [2345]
stop on runlevel [06]
respawn
respawn limit 10 5
exec /var/www/webgis/gunicorn.sh
EOF

chmod 755 /var/www/webgis/gunicorn.sh
ln -sf /lib/init/upstart-job /etc/init.d/webgis

service webgis restart
service nginx reload


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
