#
# UTILITY FUNCTIONS
#

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
	# download and install Serf
	if [ ! -f "/usr/local/bin/serf" ]; then
		# get arch from function parameter or autodetect
		if [ "$1" != "" ]; then
			serf_arch=$1
		else
			if [ "$(getconf LONG_BIT)" == "32" ]; then
				serf_arch="386"
			else
				serf_arch="amd64"
			fi
		fi

		# download Serf
		wget --no-verbose \
			--retry-connrefused \
			--waitretry=1 \
			--read-timeout=20 \
			--timeout=15 \
			--tries=0 \
			--output-document=/tmp/serf.zip https://dl.bintray.com/mitchellh/serf/0.6.4_linux_$serf_arch.zip

		# install Serf
		unzip -d /tmp /tmp/serf.zip
		mv /tmp/serf /usr/local/bin/serf
		rm -f /tmp/serf.zip
	fi
}


# vim: set ts=4 sts=4 sw=4 noet:
