#
### CLIENT INSTALLATION ###
#

# perform installation only for chosen GIS.lab suites
if [ "$GISLAB_SUITE" != "lab" ]; then
	return
fi


# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  ltsp-server-standalone
  tftpd-hpa
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES

# do not allow overriding of DHCP server configuration by LTSP, keep using configuration located in /etc/dhcp
rm -f /etc/ltsp/dhcpd.conf


source $GISLAB_INSTALL_CLIENT_ROOT/install.sh # install client image


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
