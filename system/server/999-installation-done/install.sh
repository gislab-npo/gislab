#
### INSTALLATION FINISHED ###
#

# 'installation.done' file is used to detect if we are running initial GIS.lab
# installation or we are performing upgrade
mkdir -p /etc/gislab
echo "$(gislab_config_header)" >> /etc/gislab/installation.done


# print installation summary
gislab_print_info "Installation finished"

installation_summary="
\nGENERAL INFORMATION
\n===================
\n* GIS.lab ID        : $GISLAB_UNIQUE_ID
\n* GIS.lab version   : $GISLAB_VERSION
\n
"
echo -e $installation_summary


# load provider customization file if exists
if [ -f "$GISLAB_INSTALL_CURRENT_ROOT/install-$GISLAB_SERVER_PROVIDER.sh" ]; then
	source $GISLAB_INSTALL_CURRENT_ROOT/install-$GISLAB_SERVER_PROVIDER.sh
fi


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
