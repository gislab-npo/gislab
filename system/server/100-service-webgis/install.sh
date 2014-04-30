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
cp /vagrant/system/server/100-service-webgis/conf/nginx/site-webgis /etc/nginx/sites-available/webgis
gislab_config_header_to_file /etc/nginx/sites-available/webgis
ln -sf /etc/nginx/sites-available/webgis /etc/nginx/sites-enabled/webgis

# add web alias if configured
if [ -n "$GISLAB_WEB_ALIAS" ]; then
	sed -i "s/server_name web.gis.lab;/server_name web.gis.lab $GISLAB_WEB_ALIAS;/" /etc/nginx/sites-available/webgis
fi


# Gunicorn deployment
# get number of CPU for adjusting number of Gunicorn workers
cpus=$(cat /proc/cpuinfo  | grep processor | wc -l)

if [ $cpus > 1 ]; then
	gunicorn_workers=$(echo $cpus*2 + 1 | bc)
else
	gunicorn_workers=3
fi

# Gunicorn startup script (adjust number of work)
cp /vagrant/system/server/100-service-webgis/conf/gunicorn/gunicorn.sh /var/www/webgis/gunicorn.sh
sed -i "s/NUM_WORKERS=.*/NUM_WORKERS=$gunicorn_workers/" /var/www/webgis/gunicorn.sh
chmod 755 /var/www/webgis/gunicorn.sh

# Gunicorn Upstart script
cp /vagrant/system/server/100-service-webgis/conf/upstart/webgis.conf /etc/init/webgis.conf
gislab_config_header_to_file /etc/init/webgis.conf
ln -sf /lib/init/upstart-job /etc/init.d/webgis

service webgis restart
service nginx reload


# activate backup
mkdir -p /etc/cron.d.bin
cp /vagrant/system/server/100-service-webgis/bin/gislab-backup-webgis.sh /etc/cron.d.bin
cat << EOL > /etc/cron.d/gislab-backup-webgis
$(gislab_config_header)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/vagrant/system/bin
MAILTO=root

15 2	* * *  root  nice /etc/cron.d.bin/gislab-backup-webgis.sh > /dev/null
EOL


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
