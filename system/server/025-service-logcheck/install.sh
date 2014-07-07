#
### LOGCHECK ###
#

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  logcheck
  logcheck-database
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# main logcheck configuration
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/logcheck/logcheck.conf /etc/logcheck/logcheck.conf
gislab_config_header_to_file /etc/logcheck/logcheck.conf

# list of files to check
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/logcheck/logcheck.logfiles /etc/logcheck/logcheck.logfiles
gislab_config_header_to_file /etc/logcheck/logcheck.logfiles

# logcheck cron job
cat << EOL > /etc/cron.d/logcheck
$(gislab_config_header)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root

@reboot		logcheck	if [ -x /usr/sbin/logcheck ]; then nice -n10 /usr/sbin/logcheck -R -H "[GIS.lab ID: $GISLAB_UNIQUE_ID] "; fi
2 *	* * *	logcheck	if [ -x /usr/sbin/logcheck ]; then nice -n10 /usr/sbin/logcheck -H "[GIS.lab ID: $GISLAB_UNIQUE_ID] "; fi
EOL


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
