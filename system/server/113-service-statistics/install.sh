#
###  STATS WEB PAGE (Munin)  ###
#

# configure munin master
cp /vagrant/system/server/113-service-statistics/conf/munin/munin.conf /etc/munin/munin.conf
gislab_config_header_to_file /etc/munin/munin.conf

# configure munin node
cp /vagrant/system/server/113-service-statistics/conf/munin/munin-node.conf /etc/munin/munin-node.conf
gislab_config_header_to_file /etc/munin/munin-node.conf
cp /vagrant/system/server/113-service-statistics/conf/munin/munin-node /etc/munin/plugin-conf.d/munin-node
gislab_config_header_to_file /etc/munin/plugin-conf.d/munin-node

# install munin plugin for graphing requests to mapserver
cp /vagrant/system/server/113-service-statistics/bin/apache_request_mapserver /usr/share/munin/plugins/apache_request_mapserver
chmod +x /usr/share/munin/plugins/apache_request_mapserver

# install munin plugin for graphing requests to webgis
cp /vagrant/system/server/113-service-statistics/bin/nginx_request_webgis /usr/share/munin/plugins/nginx_request_webgis
chmod +x /usr/share/munin/plugins/nginx_request_webgis

# install munin plugin for graphing cpu usage by process
cp /vagrant/system/server/113-service-statistics/bin/cpu_by_process /usr/share/munin/plugins/cpu_by_process
chmod +x /usr/share/munin/plugins/cpu_by_process

# disable all plugins
rm -f /etc/munin/plugins/*

# enable only required plugins
ln -fs /usr/share/munin/plugins/apache_request_mapserver /etc/munin/plugins/apache_request_mapserver
ln -fs /usr/share/munin/plugins/cpu /etc/munin/plugins/cpu
ln -fs /usr/share/munin/plugins/cpu_by_process /etc/munin/plugins/cpu_by_process
ln -fs /usr/share/munin/plugins/df /etc/munin/plugins/df
ln -fs /usr/share/munin/plugins/df_inode /etc/munin/plugins/df_inode
ln -fs /usr/share/munin/plugins/diskstats /etc/munin/plugins/diskstats
ln -fs /usr/share/munin/plugins/interrupts /etc/munin/plugins/interrupts
ln -fs /usr/share/munin/plugins/iostat /etc/munin/plugins/iostat
ln -fs /usr/share/munin/plugins/iostat_ios /etc/munin/plugins/iostat_ios
ln -fs /usr/share/munin/plugins/irqstats /etc/munin/plugins/irqstats
ln -fs /usr/share/munin/plugins/load /etc/munin/plugins/load
ln -fs /usr/share/munin/plugins/memory /etc/munin/plugins/memory
ln -fs /usr/share/munin/plugins/multips_memory /etc/munin/plugins/multips_memory
ln -fs /usr/share/munin/plugins/nginx_request_webgis /etc/munin/plugins/nginx_request_webgis
ln -fs /usr/share/munin/plugins/open_files /etc/munin/plugins/open_files
ln -fs /usr/share/munin/plugins/open_inodes /etc/munin/plugins/open_inodes
ln -fs /usr/share/munin/plugins/postgres_cache_ /etc/munin/plugins/postgres_cache_ALL
ln -fs /usr/share/munin/plugins/postgres_cache_ /etc/munin/plugins/postgres_cache_gislab
ln -fs /usr/share/munin/plugins/postgres_cache_ /etc/munin/plugins/postgres_cache_webgis
ln -fs /usr/share/munin/plugins/processes /etc/munin/plugins/processes
ln -fs /usr/share/munin/plugins/swap /etc/munin/plugins/swap
ln -fs /usr/share/munin/plugins/uptime /etc/munin/plugins/uptime
ln -fs /usr/share/munin/plugins/vmstat /etc/munin/plugins/vmstat

# create NGINX virtualhost stats.gis.lab
cp /vagrant/system/server/113-service-statistics/conf/nginx/site-stats /etc/nginx/sites-available/stats
gislab_config_header_to_file /etc/nginx/sites-available/stats
ln -fs /etc/nginx/sites-available/stats /etc/nginx/sites-enabled/

# remove unnecessary configuration
rm -f /etc/apache2/conf.d/munin
rm -f /etc/cron.d/munin-node

# launch munin by cron
cat << EOF > /etc/cron.d/munin
MAILTO=root

*/5 *	* * *	munin	if [ -x /usr/bin/munin-cron ]; then /usr/bin/munin-cron; fi
EOF
gislab_config_header_to_file /etc/cron.d/munin

# restart services
service apache2 restart
service nginx restart
service munin-node restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
