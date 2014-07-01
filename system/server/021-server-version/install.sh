#
### SERVER VERSION ###
#

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  git
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# version
# set version from Git if we are running from sources
if [ -d "/vagrant/.git" ]; then
	GISLAB_VERSION_BRANCH=$(git --git-dir=/vagrant/.git --work-tree=/vagrant rev-parse --abbrev-ref HEAD)
	GISLAB_VERSION_CHANGESET=$(git --git-dir=/vagrant/.git --work-tree=/vagrant rev-parse --short HEAD)
	GISLAB_VERSION=git+$GISLAB_VERSION_BRANCH+$GISLAB_VERSION_CHANGESET

	GISLAB_VERSION_TAG=$(git --git-dir=/vagrant/.git --work-tree=/vagrant describe --tags --exact-match 2> /dev/null || true)
	if [ "$GISLAB_VERSION_TAG" != "" ]; then
		GISLAB_VERSION=$GISLAB_VERSION~$GISLAB_VERSION_TAG
	fi
fi

echo -e "$(gislab_config_header)" > /etc/gislab_version
echo -e "GISLAB_UNIQUE_ID='$GISLAB_UNIQUE_ID'" >> /etc/gislab_version
echo -e "GISLAB_VERSION='$GISLAB_VERSION'" >> /etc/gislab_version
echo -e "GISLAB_SERVER_BUILD_TIME='$(date)'" >> /etc/gislab_version


# update also first line of motd with some version information
sudo rm -rf /etc/update-motd.d/10-help-text
sudo rm -rf /etc/update-motd.d/51-cloudguest
sudo rm -rf /etc/update-motd.d/98-cloudguest

sed -i "s/Welcome to.*/Welcome to GIS.lab $GISLAB_VERSION ID: $GISLAB_UNIQUE_ID.\"/" /etc/update-motd.d/00-header


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
