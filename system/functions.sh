#
# UTILITY FUNCTIONS
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


gislab_print_info () {
	# print informative message
	echo -e "$(tput bold)[GIS.lab]: ${1}.$(tput sgr0)"
}


gislab_print_warning () {
	# print warning message
	echo -e "$(tput bold)$(tput setaf 5)[GIS.lab]: ${1}!$(tput sgr0)"
}


gislab_print_error () {
	# print error message
	echo -e "$(tput bold)$(tput setaf 1)[GIS.lab]: ${1}!$(tput sgr0)"
}


gislab_require_root () {
	if [[ $EUID -ne 0 ]]; then
		gislab_print_error "This command can be run only with superuser privileges"
		exit 1
	fi
}


# vim: set ts=4 sts=4 sw=4 noet: