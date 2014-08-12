#
### NTP SERVER ###
#
# Install and configure time server for all network members.


# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  ntp
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# main configuration
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/ntp/ntp.conf /etc/ntp.conf
gislab_config_header_to_file /etc/ntp.conf

service ntp restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
