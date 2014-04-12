#
# FUNCTIONS
#

gislab_config_header () {
	# print informative text about creation of configuration
	# file by GIS.lab install
	if [ -z "$1" ]; then
		c="#"
	else
		c="$1"
	fi

	echo "${c} This file was generated or modified by GIS.lab management script ($(date))."

}


# vim: set ts=4 sts=4 sw=4 noet:
