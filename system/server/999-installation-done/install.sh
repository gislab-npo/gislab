#
### INSTALLATION DONE ###
#


# 'installation.done' file is used to detect if we are running initial GIS.lab
# installation or we are performing upgrade
echo "$(gislab_config_header)" >> /var/lib/gislab/installation.done


# print installation summary
gislab_print_info "Installation finished"

installation_summary="
\nGENERAL INFORMATION
\n===================
\n* GIS.lab ID        : $GISLAB_UNIQUE_ID
\n* GIS.lab version   : $GISLAB_VERSION
"
echo -e $installation_summary


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
