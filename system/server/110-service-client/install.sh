#
### CLIENT INSTALLATION ###
#

# do not install client if GISLAB_SUITE="server"
if [ "$GISLAB_SUITE" == "server" ]; then
	return
fi

bash /vagrant/system/client/install.sh # install client image


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
