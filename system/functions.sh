#
# UTILITY FUNCTIONS
#

### PATH VARIABLES
GISLAB_PATH_ADMIN="$GISLAB_ROOT/admin"
GISLAB_PATH_CUSTOM="$GISLAB_ROOT/custom"
GISLAB_PATH_SECRET="$GISLAB_ROOT/secret"
GISLAB_PATH_SYSTEM="$GISLAB_ROOT/system"
GISLAB_PATH_STORAGE="/storage"
GISLAB_PATH_APPLICATIONS="$GISLAB_PATH_STORAGE/applications"
GISLAB_PATH_BACKUP="$GISLAB_PATH_STORAGE/backup"
GISLAB_PATH_CACHE="$GISLAB_PATH_STORAGE/cache"
GISLAB_PATH_HOME="$GISLAB_PATH_STORAGE/home"
GISLAB_PATH_LOG="$GISLAB_PATH_STORAGE/log"
GISLAB_PATH_WWW="/var/www/default"


### FUNCTIONS
gislab_info () {
    # print informative message
    m=$(echo $1 | sed "s/\n//g")

    tput bold
    echo -e "${m}." | fold -s | sed "s/^/[GIS.lab]: /g"
    tput sgr0
}


gislab_success () {
    # print success message
    m=$(echo $1 | sed "s/\n//g")

    tput bold
    tput setaf 2
    echo -e "${m}." | fold -s | sed "s/^/[GIS.lab]: /g"
    tput sgr0
}


gislab_warning () {
    # print warning message
    m=$(echo $1 | sed "s/\n//g")

    tput bold
    tput setaf 5
    echo -e "${m}!" | fold -s | sed "s/^/[GIS.lab]: /g"
    tput sgr0
}


gislab_error () {
    # print error message
    m=$(echo $1 | sed "s/\n//g")

    tput bold
    tput setaf 1
    echo -e "${m}!" | fold -s | sed "s/^/[GIS.lab]: /g"
    tput sgr0

    exit 1
}


gislab_require_root () {
    # exit if user is not root
    if [[ $EUID -ne 0 ]]; then
        gislab_error "This command can only be be run with superuser privileges"
        exit 1
    fi
}


gislab_serf_install () {
    # download and install Serf for GIS.lab cluster management

    SERF_VERSION="0.7.0"
    SERF_URL="http://gislab-software.s3.amazonaws.com"
    SERF_INSTALL="yes"

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
        wget --continue \
            --no-verbose \
            --retry-connrefused \
            --waitretry=1 \
            --read-timeout=20 \
            --timeout=15 \
            --tries=0 \
            --output-document=/storage/cache/packages/tar/${SERF_VERSION}_linux_${SERF_ARCH}.zip \
        ${SERF_URL}/serf_${SERF_VERSION}_linux_${SERF_ARCH}.zip

        # install Serf
        rm -f /usr/local/bin/serf
        unzip \
            -d /usr/local/bin \
            /storage/cache/packages/tar/${SERF_VERSION}_linux_${SERF_ARCH}.zip

        chown root:gislabadmins /usr/local/bin/serf 2> /dev/null
        chmod 774 /usr/local/bin/serf
        ln -sf /usr/local/bin/serf /usr/local/bin/gislab-cluster

        # test Serf installation
        if [ "$(serf version | grep '^Serf')" == "Serf v${SERF_VERSION}" ]; then
            echo "Serf was successfully installed (ARCH: $SERF_ARCH, VERSION: $SERF_VERSION) !"
        else
            echo "Serf installation failed !"
            exit 1
        fi
    fi
}

# vim: set ts=8 sts=4 sw=4 et:
