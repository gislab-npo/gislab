#
### GIS.LAB WEB ###
#

# Logging: 
#   production: /var/log/nginx/webgis-access.log /var/log/nginx/webgis-error.log /var/log/syslog
#   debug:      /var/log/nginx/webgis-access.log /var/log/nginx/webgis-error.log /var/log/syslog

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  gcc
  nginx
  python-dateutil
  python-dev
  python-pip
  python-psycopg2
  python-virtualenv
  pwgen
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# create database and user only on initial installation
if [ ! -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then
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
cp -a $GISLAB_INSTALL_CURRENT_ROOT/app/gislab-web $GISLAB_INSTALL_WEBGIS_DIR
pip install --download-cache=/var/cache/pip --requirement=$GISLAB_INSTALL_WEBGIS_DIR/requirements.txt
pip install gunicorn
python $GISLAB_INSTALL_WEBGIS_DIR/setup.py install > /dev/null
rm -r $GISLAB_INSTALL_WEBGIS_DIR


# install webgis
rm -rf /var/www/webgis
mkdir -p /var/www/webgis
django-admin.py startproject --template=$GISLAB_INSTALL_CURRENT_ROOT/app/gislab-web/webgis/conf/project_template/ djproject /var/www/webgis

# move map cache to /storage
mkdir -p /storage/webgis-media
chown www-data:www-data /storage/webgis-media
sed -i "s/MEDIA_ROOT =.*/MEDIA_ROOT = '\/storage\/webgis-media'/" /var/www/webgis/djproject/settings.py


# secrets
if [ ! -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then
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
	mkdir -p /etc/gislab/webgis
	cp /var/www/webgis/djproject/settings_secret.py /etc/gislab/webgis/settings_secret.py
else
	# on upgrade load secrets file from backup
	cp /etc/gislab/webgis/settings_secret.py /var/www/webgis/djproject/settings_secret.py
fi

python /var/www/webgis/manage.py syncdb --noinput
python /var/www/webgis/manage.py collectstatic --noinput > /dev/null
deactivate


# web server
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/nginx/site-webgis /etc/nginx/sites-available/webgis
gislab_config_header_to_file /etc/nginx/sites-available/webgis
ln -sf /etc/nginx/sites-available/webgis /etc/nginx/sites-enabled/webgis


# Gunicorn deployment
# get number of CPU for adjusting number of Gunicorn workers
cpus=$(cat /proc/cpuinfo  | grep processor | wc -l)

if [ $cpus > 1 ]; then
	gunicorn_workers=$(echo $cpus*2 + 1 | bc)
else
	gunicorn_workers=3
fi

# Gunicorn startup script
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/gunicorn/gunicorn.sh /var/www/webgis/gunicorn.sh
chmod 755 /var/www/webgis/gunicorn.sh

# adjust number of workers
sed -i "s/NUM_WORKERS=.*/NUM_WORKERS=$gunicorn_workers/" /var/www/webgis/gunicorn.sh

# configure logging
if [ "$GISLAB_DEBUG_SERVICES" == "no" ]; then
	sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=error/" /var/www/webgis/gunicorn.sh
else
	sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=debug/" /var/www/webgis/gunicorn.sh
fi

# Gunicorn Upstart script
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/upstart/webgis.conf /etc/init/webgis.conf
gislab_config_header_to_file /etc/init/webgis.conf
ln -sf /lib/init/upstart-job /etc/init.d/webgis

service webgis restart
service nginx reload

# cache cleanup job
cat << EOL > /etc/cron.d/gislab-webgis-mapcache-clean
$(gislab_config_header)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:$GISLAB_ROOT/system/bin
MAILTO=root

15 0	* * *  www-data  nice /usr/local/python-virtualenvs/webgis/bin/python /var/www/webgis/manage.py mapcache_clean > /dev/null
EOL


### LOGGING ###
# check logs with logcheck
echo "/var/log/nginx/webgis-error.log" >> /etc/logcheck/logcheck.logfiles


### BACKUP ###
mkdir -p /etc/cron.d.bin
cp $GISLAB_INSTALL_CURRENT_ROOT/bin/gislab-backup-webgis.sh /etc/cron.d.bin
cat << EOL > /etc/cron.d/gislab-backup-webgis
$(gislab_config_header)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:$GISLAB_ROOT/system/bin
MAILTO=root

15 2	* * *  root  nice /etc/cron.d.bin/gislab-backup-webgis.sh > /dev/null
EOL


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
