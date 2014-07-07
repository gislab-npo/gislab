#
### DATABASE SERVER - POSTGRESQL/POSTGIS ###
#

# Logging: 
#   production: /var/log/postgresql/postgresql-error.log
#   debug:      /var/log/postgresql/postgresql-debug.log

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  pgtune
  postgis
  postgresql
  postgresql-9.1-postgis-2.1
  postgresql-comparator
  postgresql-contrib
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# set system shmmax value which must be something little bit higher than one fourth of
# system memory size
shmmax=$(echo $(free -b | awk '/^Mem:/{print $2}') / 3.5 | bc)
sysctl -w kernel.shmmax=$shmmax
cat << EOF > /etc/sysctl.d/30-postgresql-shm.conf
$(gislab_config_header)
kernel.shmmax = $shmmax
EOF

# access policy
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/postgresql/pg_hba.conf /etc/postgresql/9.1/main/pg_hba.conf
gislab_config_header_to_file /etc/postgresql/9.1/main/pg_hba.conf

# main database configuration
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/postgresql/postgresql.conf /etc/postgresql/9.1/main/postgresql.conf
gislab_config_header_to_file /etc/postgresql/9.1/main/postgresql.conf

# tune database depending on current server configuration
pgtune -T Mixed -i /etc/postgresql/9.1/main/postgresql.conf -o /etc/postgresql/9.1/main/postgresql.conf


### LOGGING ###
if [ "$GISLAB_DEBUG_SERVICES" == "no" ]; then
	cat << EOF >> /etc/postgresql/9.1/main/postgresql.conf
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-error.log'
log_min_messages = FATAL
EOF
else
	cat << EOF >> /etc/postgresql/9.1/main/postgresql.conf
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-debug.log'
log_min_messages = 'DEBUG1'
log_min_error_statement = 'DEBUG1'
log_min_duration_statement = 0
EOF
fi

# remove default log file
rm -f /var/log/postgresql/postgresql-9.1-main.log

# create default log file
touch /var/log/postgresql/postgresql-error.log
chmod 0640 /var/log/postgresql/postgresql-error.log
chown postgres:adm /var/log/postgresql/postgresql-error.log

# check logs with logcheck
echo "/var/log/postgresql/postgresql-error.log" >> /etc/logcheck/logcheck.logfiles

service postgresql restart


### DO NOT CONTINUE ON UPGRADE ###
if [ -f "/etc/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then return; fi

# create labusers and labadmins group
sudo su - postgres -c "createuser --no-superuser --no-createdb --no-createrole --no-login labusers"
sudo su - postgres -c "createuser --superuser --createdb --createrole --no-login labadmins"

# create template database
sudo su - postgres -c "createdb -E UTF8 -T template0 template_postgis"
sudo su - postgres -c "psql -d template_postgis -c \"CREATE EXTENSION postgis;\""
sudo su - postgres -c "psql -d template_postgis -c \"CREATE EXTENSION postgis_topology;\""

sudo su - postgres -c "psql -d template_postgis -c \"REVOKE ALL ON SCHEMA public FROM PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT USAGE ON SCHEMA public TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT ALL ON SCHEMA public TO postgres;\""

sudo su - postgres -c "psql -d template_postgis -c \"GRANT SELECT, UPDATE, INSERT, DELETE ON geometry_columns TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT SELECT, UPDATE, INSERT, DELETE ON geography_columns TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT SELECT, UPDATE, INSERT, DELETE ON spatial_ref_sys TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT USAGE ON SCHEMA topology TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT SELECT, UPDATE, INSERT, DELETE ON layer TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT SELECT, UPDATE, INSERT, DELETE ON topology TO PUBLIC;\""

# add postgresql-comparator support
sudo su - postgres -c "psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/pgc_checksum.sql"
sudo su - postgres -c "psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/pgc_casts.sql"
sudo su - postgres -c "psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/xor_aggregate.sql"

# add history audit support (run SELECT audit.audit_table('<schema>.<table>'); to enable)
sudo su - postgres -c "psql -d template_postgis -f $GISLAB_INSTALL_CURRENT_ROOT/app/audit-trigger/audit.sql"
sudo su - postgres -c "psql -d template_postgis -c \"CREATE EXTENSION IF NOT EXISTS hstore;\""

# close template database
sudo su - postgres -c "psql -d template_postgis -c \"VACUUM FULL;\""
sudo su - postgres -c "psql -d template_postgis -c \"VACUUM FREEZE;\""
sudo su - postgres -c "psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\""
sudo su - postgres -c "psql -d postgres -c \"UPDATE pg_database SET datallowconn='false' WHERE datname='template_postgis';\""

# create gislab database
sudo su - postgres -c "createdb -T template_postgis gislab"
sudo su - postgres -c "psql -c \"GRANT CONNECT ON DATABASE gislab TO labusers;\""


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
