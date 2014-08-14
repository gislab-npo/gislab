#
### MAPSERVER WORKER ###
#
# Create a package for mapserver worker instances installation in cloud environment. Installation
# package consist from installation script and other files needed for server configuration. To use it
# run following commands on newly launched instance (in Amazon AWS use 'clod-data' for commands injection):
# $ mkdir /tmp/install-worker && cd /tmp/install-worker && \
#   curl http://<GISLAB_SERVER_IP>/worker.tar.gz | tar xz -C /tmp/install-worker && \
#   bash ./install.sh && rm -rf /tmp/install-worker


GISLAB_WORKER_IMAGE_ROOT=/opt/worker
export GISLAB_WORKER_IMAGE_ROOT

GISLAB_WORKER_IMAGE_BASE=$GISLAB_WORKER_IMAGE_ROOT/base
export GISLAB_WORKER_IMAGE_BASE

rm -rf $GISLAB_WORKER_IMAGE_ROOT
mkdir -p $GISLAB_WORKER_IMAGE_ROOT $GISLAB_WORKER_IMAGE_BASE


GISLAB_WORKER_INSTALL_PACKAGES="
    apache2
    apache2-mpm-worker
    htop
    libapache2-mod-fastcgi
    mc
    munin-node
    nfs-common
    python-gdal
    python-qgis
    pwgen
    qgis
    qgis-mapserver
    unzip
    vim
"
GISLAB_WORKER_INSTALL_PACKAGES=$(echo $GISLAB_WORKER_INSTALL_PACKAGES) # this is needed to remove newlines
export GISLAB_WORKER_INSTALL_PACKAGES

source $GISLAB_INSTALL_WORKER_ROOT/install.sh # install worker package


# vim: set ts=4 sts=4 sw=4 noet:
