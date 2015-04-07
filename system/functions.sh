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
	# download and install Serf for GIS.lab cluster management

	SERF_INSTALL="yes"
	SERF_VERSION="$1"
		
	# detect architecture
	if [ "$(getconf LONG_BIT)" == "32" ]; then
		SERF_ARCH="386"
	else
		SERF_ARCH="amd64"
	fi

	# test if installation is required
	if ! type "serf" > /dev/null 2>&1; then
		echo "Serf is not installed. Performing installation ..."

	else
		echo "Serf is installed. Checking version ..."

		if [ "$SERF_VERSION" == "" ]; then
			echo "Version not given !"
			exit 1
		fi

		if [ "$(serf version | grep '^Serf')" == "Serf v${SERF_VERSION}" ]; then
			echo "Serf installation is up to date !"
			SERF_INSTALL="no"
		else
			echo "Serf installation is outdated. Updating ..."
		fi
	fi

	# perform installation if required
	if [ "$SERF_INSTALL" == "yes" ]; then
		# download Serf
		wget --no-verbose \
			--retry-connrefused \
			--waitretry=1 \
			--read-timeout=20 \
			--timeout=15 \
			--tries=0 \
			--output-document=/tmp/serf.zip https://dl.bintray.com/mitchellh/serf/${SERF_VERSION}_linux_${SERF_ARCH}.zip

		# install Serf
		rm -f /usr/local/bin/serf
		unzip -d /usr/local/bin /tmp/serf.zip
		rm -f /tmp/serf.zip

		chown root:root /usr/local/bin/serf
		chmod 744 /usr/local/bin/serf

		echo "Serf was successfully installed (ARCH: $SERF_ARCH, VERSION: $SERF_VERSION)!"
	fi
}


# vim: set ts=4 sts=4 sw=4 noet:
