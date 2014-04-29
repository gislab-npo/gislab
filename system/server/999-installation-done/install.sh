#
### INSTALLATION FINISHED ###
#

# 'installation.done' file is used to detect if we are running initial GIS.lab
# installation or we are performing upgrade
mkdir -p /etc/gislab
echo "$(gislab_config_header)" >> /etc/gislab/installation.done


installation_summary="
GIS.lab is installed and ready to use!
\n
\nGENERAL INFORMATION
\n===================
\n* GIS.lab ID        : $GISLAB_UNIQUE_ID
\n* GIS.lab version   : $GISLAB_VERSION
\n
"

# append AWS information if running on AWS
if [ "$GISLAB_SERVER_PROVIDER" == "aws" ]; then
	installation_summary+="\nAMAZON WEB SERVICES"
	installation_summary+="\n==================="
	installation_summary+="\n* Instance ID        : $GISLAB_SERVER_AWS_INSTANCE_ID"
	installation_summary+="\n* Public IP          : $GISLAB_SERVER_AWS_PUBLIC_IP"
	installation_summary+="\n* Public hostname    : $GISLAB_SERVER_AWS_PUBLIC_HOSTNAME"
fi

# print installation summary
gislab_print_info "Installation finished"
echo -e $installation_summary

# send installation summary to administrator by email
echo -e $installation_summary | mail -s "[GIS.lab ID: $GISLAB_UNIQUE_ID] Installation done" root


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
