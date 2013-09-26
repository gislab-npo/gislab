#!/bin/bash
# Vagrant shell provisioner script. DO NOT RUN BY HAND.
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

# LTSP troubleshooting https://help.ubuntu.com/community/UbuntuLTSP/ClientTroubleshooting

set -e


GISLAB_VERSION=0.1~dev

#
### SERVER UPGRADE ###
#
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8
locale-gen en_US.UTF-8

cat << EOF >> /etc/default/locale
LANG="en_US.UTF-8"
LANGUAGE="en_US:en"
EOF

export DEBIAN_FRONTEND=noninteractive
echo "PATH="$PATH:/vagrant/bin"" >> /etc/profile


# hold kernel packages from upgrade to avoid a need to restart server after
# installation (Vagrant box could provide up-to-date kernel image)
echo "linux-image-$(uname -r) hold" | dpkg --set-selections
echo "linux-generic-pae hold" | dpkg --set-selections
echo "linux-image-generic-pae hold" | dpkg --set-selections

echo "grub-pc hold" | dpkg --set-selections # hold also grub because of some issue

# set apt-cacher if available
#sed -i "s/deb http:\/\//deb http:\/\/<APT-CACHER IP>:3142\//" /etc/apt/sources.list

apt-get update
apt-get --assume-yes upgrade
apt-get --assume-yes install htop vim mc --no-install-recommends
apt-get --assume-yes install postgresql postgis postgresql-9.1-postgis nfs-kernel-server

apt-get --assume-yes install ltsp-server-standalone openssh-server isc-dhcp-server tftpd-hpa --no-install-recommends




#
### DHCP ###
#
cat << EOF > /etc/ltsp/dhcpd.conf
authoritative;

subnet 192.168.50.0 netmask 255.255.255.0 {
    range 192.168.50.100 192.168.50.250;
    option domain-name "gislab.lan";
    option domain-name-servers 8.8.8.8;
    option broadcast-address 192.168.50.255;
    option routers 192.168.50.5;
    option subnet-mask 255.255.255.0;
    option root-path "/opt/ltsp/i386";
    if substring( option vendor-class-identifier, 0, 9 ) = "PXEClient" {
        filename "/ltsp/i386/pxelinux.0";
    } else {
        filename "/ltsp/i386/nbi.img";
    }
}
EOF

cat << EOF > /etc/default/isc-dhcp-server
INTERFACES="eth1"
EOF


# set IP forwarding for LTSP clients and call it from rc.local to run it after server restart
cat << EOF > /usr/local/bin/enable-ip-forward
#!/bin/bash

sysctl -w net.ipv4.ip_forward=1
iptables --table nat --append POSTROUTING --jump MASQUERADE --source 192.168.50.0/24
EOF

chmod +x /usr/local/bin/enable-ip-forward
/usr/local/bin/enable-ip-forward

sed -i "s/exit 0//" /etc/rc.local
echo "/usr/local/bin/enable-ip-forward" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local

service isc-dhcp-server restart




#
### LTSP ###
#
echo "deb http://ppa.launchpad.net/imincik/gis/ubuntu precise main" >> /etc/apt/sources.list # add extra GIS repository
echo "deb http://ppa.launchpad.net/imincik/qgis2/ubuntu precise main" >> /etc/apt/sources.list # add extra QGIS 2 repository

# add some ltsp-build-client plugins which takes care about our image customizations
rm -vf /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/*gislab*
cp -av /vagrant/config/ltsp/plugins/ltsp-build-client/* /usr/share/ltsp/plugins/ltsp-build-client/Ubuntu/

# client image configuration
cat << EOF > /etc/ltsp/ltsp-build-client.conf
GISLAB_VERSION=$GISLAB_VERSION
ARCH=i386
FAT_CLIENT_DESKTOPS="xubuntu-desktop"
LATE_PACKAGES="
    nfs-common
    aptitude
    htop
    mc
    rst2pdf
    libreoffice
    libreoffice-gtk
    libreoffice-calc
    libreoffice-writer
    gimp
    flashplugin-installer
    pgadmin3
    qgis
    python-qgis
    qgis-plugin-grass
    grass
    gdal-bin
    libgdal1h
    python-gdal
    sqlite3
    spatialite-bin
    spatialite-gui
    git
    vim-gnome
    ipython
    postgresql-client
"
REMOVE_PACKAGES="
    thunderbird-globalmenu
    abiword
    abiword-common
    abiword-plugin-grammar
    abiword-plugin-mathview
    libabiword-2.9
    gnumeric
    gnumeric-common
    gnumeric-doc
"
EOF

ltsp-build-client --purge-chroot --copy-sourceslist --accept-unsigned-packages  # use --mirror http://<URL>:3142/sk.archive.ubuntu.com/ubuntu
																			    # or use --mount-package-cache --keep-packages to use local cache
ltsp-update-sshkeys
ltsp-update-kernels

# LTSP configuration
cat << EOF > /var/lib/tftpboot/ltsp/i386/lts.conf
[default]
LDM_SESSION=/usr/bin/startxfce4
CLIENT_ENV="DESKTOP_SESSION=xubuntu"
LDM_THEME=gislab 
LOCAL_APPS=True
SCREEN_02=shell                          # get local root prompt when pressing Ctrl+Alt+F2 
SCREEN_07=ldm
FSTAB_0="server:/home /home nfs defaults 0 0"
FSTAB_1="server:/storage /mnt nfs defaults 0 0"
EOF

service nbd-server restart

# disable plymouth screen for better client troubleshooting on boot
sed -i "s/splash plymouth:force-splash vt.handoff=7//" /var/lib/tftpboot/ltsp/i386/pxelinux.cfg/default




#
### NFS Share ###
#
mkdir -p /storage/share
mkdir -p /storage/share/data	# writable only for superuser
mkdir -p /storage/share/pub		# writable for NFS users
chown nobody:nogroup /storage/share/pub
chmod ugo+rwx /storage/share/pub

cat << EOF > /etc/exports
/home                       *(rw,sync,no_subtree_check)
/storage                    *(rw,sync,no_subtree_check,all_squash,insecure)
EOF

service nfs-kernel-server restart




#
#### PostgreSQL ###
#
# allow network connections and local connection without password
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/9.1/main/postgresql.conf
sed -i "s/local.*all.*all.*peer/local  all  all  trust/" /etc/postgresql/9.1/main/pg_hba.conf
sed -i "s/host.*all.*all.*127.0.0.1\/32.*md5/host  all  all  0.0.0.0\/0  md5/" /etc/postgresql/9.1/main/pg_hba.conf
service postgresql restart

# create users
sudo -u postgres createuser --superuser labadmin
sudo -u postgres createuser --no-superuser --no-createdb --no-createrole lab
sudo -u postgres psql -c "ALTER ROLE lab WITH PASSWORD 'lab'"

# create template database
createdb -U labadmin -E UTF8 -T template0 template_postgis
psql -U labadmin -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
psql -U labadmin -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
psql -U labadmin -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
psql -U labadmin -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
psql -U labadmin -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
psql -U labadmin -d template_postgis -c "VACUUM FULL;"
psql -U labadmin -d template_postgis -c "VACUUM FREEZE;"
psql -U labadmin -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
psql -U labadmin -d postgres -c "UPDATE pg_database SET datallowconn='false' WHERE datname='template_postgis';"

# create gislab database
createdb -U labadmin -O labadmin -T template_postgis gislab




#
### USERS ###
#
/vagrant/bin/gislab-addusers.sh # call script to create user accounts


# vim: set ts=4 sts=4 sw=4 noet:
