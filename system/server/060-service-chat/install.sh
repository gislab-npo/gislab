#
### IRC SERVER ###
#

# Logging: 
#   production: /var/log/ircd/ircd-hybrid.log
#   debug:      /var/log/ircd/ircd-hybrid.log

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  ircd-hybrid
  irssi
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# IRC server configuration
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/ircd/ircd.conf /etc/ircd-hybrid/ircd.conf
gislab_config_header_to_file /etc/ircd-hybrid/ircd.conf

cat << EOF > /etc/ircd-hybrid/ircd.motd
Welcome to GIS.lab IRC server !
EOF

service ircd-hybrid restart


### LOGGING ###
cp $GISLAB_INSTALL_DIR/$GISLAB_INSTALL_CURRENT_DIR/conf/logrotate/ircd-hybrid /etc/logrotate.d/ircd-hybrid
gislab_config_header_to_file /etc/logrotate.d/ircd-hybrid

chmod 0640 /var/log/ircd/ircd-hybrid.log
chgrp adm /var/log/ircd/ircd-hybrid.log

# check logs with logcheck
echo "/var/log/ircd/ircd-hybrid.log" >> /etc/logcheck/logcheck.logfiles


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
