#
### PROVIDER CUSTOMIZATIONS ###
#

# load provider customization file if exists
if [ -f "$GISLAB_INSTALL_CURRENT_ROOT/install-$GISLAB_SERVER_PROVIDER.sh" ]; then
	source $GISLAB_INSTALL_CURRENT_ROOT/install-$GISLAB_SERVER_PROVIDER.sh
fi


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
