#
# UTILITY FUNCTIONS
#

gislab_config () {
	# read default config file
	source $GISLAB_ROOT/config.cfg
	
	if [ -f $GISLAB_ROOT/config-user.cfg ]
	then
		source $GISLAB_ROOT/config-user.cfg
	fi
}

gislab_config_header () {
	# print informative text about creation of configuration
	# file by GIS.lab install
	if [ -z "$1" ]; then
		c="#"
	else
		c="$1"
	fi

	echo "${c} This file was created or modified by GIS.lab $GISLAB_VERSION on $(date)."
}


gislab_config_header_to_file () {
	# write output of 'gislab_config_header' to first line of given file
	if [ $# -eq 1 ]; then
		sed -i -e "1i $(echo $(gislab_config_header)) " $1
	elif [ $# -eq 2 ]; then
		sed -i -e "1i $(echo $(gislab_config_header $1)) " $2
	fi
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
	exit 1
}


gislab_require_root () {
	# exit if user is not root
	if [[ $EUID -ne 0 ]]; then
		gislab_print_error "This command can only be be run with superuser privileges"
		exit 1
	fi
}


gislab_serf_install () {
	if [ ! -f "/usr/local/bin/serf" ]; then
		# download and install Serf
		if [ "$(uname -i)" == "i386" ]; then
			serf_arch="386"
		else
			serf_arch="amd64"
		fi

		until wget -O /tmp/serf.zip https://dl.bintray.com/mitchellh/serf/0.6.3_linux_$serf_arch.zip; do
			sleep 1
		done

		unzip -d /tmp /tmp/serf.zip
		mv /tmp/serf /usr/local/bin/serf
		rm -f /tmp/serf.zip
	fi
}


# vim: set ts=4 sts=4 sw=4 noet:
