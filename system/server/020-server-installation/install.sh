#
### SERVER INSTALLATION ###
#
# Configure installation repositories and install basic server software.


export DEBIAN_FRONTEND=noninteractive

# use Ubuntu repositories provided by AWS if running in AWS
if [ "$GISLAB_SERVER_PROVIDER" == "aws" ]; then
	GISLAB_APT_REPOSITORY_COUNTRY_MIRROR_MAIN="${GISLAB_SERVER_AWS_REGION}.ec2"
else
	GISLAB_APT_REPOSITORY_COUNTRY_MIRROR_MAIN="$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR"
fi

# Main Ubuntu repositories
cat << EOF > /etc/apt/sources.list
$(gislab_config_header)

###### Main Ubuntu repositories
deb http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR_MAIN.archive.ubuntu.com/ubuntu/ precise main universe multiverse 
deb http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR_MAIN.archive.ubuntu.com/ubuntu/ precise-updates main universe multiverse 

EOF

cat << EOF >> /etc/apt/sources.list
###### Ubuntu security updates
deb http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR.archive.ubuntu.com/ubuntu/ precise-security main universe multiverse 

###### Ubuntu partner repository
deb http://archive.canonical.com/ubuntu precise partner

EOF

cat << EOF >> /etc/apt/sources.list
#### GIS.lab GIS repository
deb http://ppa.launchpad.net/imincik/gis/ubuntu precise main

EOF

# custom QGIS repository
if [ -n "${GISLAB_QGIS_REPOSITORY}" ]; then
	cat << EOF >> /etc/apt/sources.list
#### $GISLAB_QGIS_REPOSITORY
deb http://ppa.launchpad.net/$GISLAB_QGIS_REPOSITORY/ubuntu precise main

EOF
fi

apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6CD44B55 # add imincik PPA key

# JOSM repository
cat << EOF >> /etc/apt/sources.list
#### JOSM
deb http://josm.openstreetmap.de/apt precise universe

EOF
wget -q http://josm.openstreetmap.de/josm-apt.key -O- | sudo apt-key add - # add JOSM repository key

# Google repositories
cat << EOF >> /etc/apt/sources.list
#### Google Chrome Browser - http://www.google.com/linuxrepositories/
deb http://dl.google.com/linux/chrome/deb/ stable main

#### Google Earth - http://www.google.com/linuxrepositories/
deb http://dl.google.com/linux/earth/deb/ stable main
EOF
wget -q https://dl-ssl.google.com/linux/linux_signing_key.pub -O- | sudo apt-key add - # add Google repositories key


# use APT proxy on server if configured and provider is not AWS (AWS is using AWS hosted repositories)
if [[ -n "${GISLAB_APT_HTTP_PROXY}" && "${GISLAB_SERVER_PROVIDER}" != "aws" ]]; then
	cat << EOF > /etc/apt/apt.conf.d/02proxy
$(gislab_config_header)
Acquire::http { Proxy "$GISLAB_APT_HTTP_PROXY"; };
EOF
else
	rm -f /etc/apt/apt.conf.d/02proxy
fi


# remove linux header which doesn't match current kernel
dpkg-query -W -f='${PackageSpec} ${Status}\n' linux-headers* \
	| grep "install ok installed" \
	| grep -v "linux-headers-$(uname -r)" \
	| awk -F " " '{print $1}' \
	| xargs  apt-get --assume-yes --force-yes purge

# Hold kernel packages from upgrade to avoid a need to restart server after
# installation (Vagrant box could provide up-to-date kernel image).
# If some package still triggers system restart check '/var/run/reboot-required.pkgs'.
# TODO: use more recent way of holding packages (apt-mark hold)
echo "linux-image-$(uname -r) hold" | dpkg --set-selections
echo "linux-generic-pae hold" | dpkg --set-selections
echo "linux-image-generic-pae hold" | dpkg --set-selections

# hold also grub because of some issue
echo "grub-pc hold" | dpkg --set-selections

# hold also virtualbox guest packages to avoid module upgrade
echo "virtualbox-guest-utils hold" | dpkg --set-selections
echo "virtualbox-guest-x11 hold" | dpkg --set-selections


# initial packages installation
apt-get update
apt-get --assume-yes --force-yes upgrade

GISLAB_SERVER_INSTALL_PACKAGES="
  htop
  mc
  ntp
  tmux
  vim
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
