#!/bin/bash
# Vagrant shell provisioner script. DO NOT RUN BY HAND.
# Author Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com

# LTSP troubleshooting https://help.ubuntu.com/community/UbuntuLTSP/ClientTroubleshooting

set -e

source /vagrant/config.cfg
if [ -f /vagrant/config-user.cfg ]
then
	source /vagrant/config-user.cfg
fi

GISLAB_VERSION=dev

if [ "$GISLAB_DEBUG" == "yes" ];
then
	set -x
fi

#
### BASIC SERVER SETTINGS
#
# timezone
cat << EOF > /etc/timezone
$GISLAB_TIMEZONE
EOF

dpkg-reconfigure --frontend noninteractive tzdata


# locales
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8
locale-gen en_US.UTF-8

cat << EOF > /etc/default/locale
LANG="en_US.UTF-8"
LANGUAGE="en_US:en"
EOF




#
### SERVER UPGRADE ###
#
export DEBIAN_FRONTEND=noninteractive
echo "PATH="$PATH:/vagrant/system/bin"" >> /etc/profile

cat << EOF > /etc/apt/sources.list
#############################################################
################### OFFICIAL UBUNTU REPOS ###################
#############################################################

###### Ubuntu Main Repos
deb http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR.archive.ubuntu.com/ubuntu/ precise main restricted universe multiverse 
deb-src http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR.archive.ubuntu.com/ubuntu/ precise main restricted universe multiverse 

###### Ubuntu Update Repos
deb http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR.archive.ubuntu.com/ubuntu/ precise-security main restricted universe multiverse 
deb http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR.archive.ubuntu.com/ubuntu/ precise-updates main restricted universe multiverse 
deb-src http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR.archive.ubuntu.com/ubuntu/ precise-security main restricted universe multiverse 
deb-src http://$GISLAB_APT_REPOSITORY_COUNTRY_MIRROR.archive.ubuntu.com/ubuntu/ precise-updates main restricted universe multiverse 

###### Ubuntu Partner Repo
deb http://archive.canonical.com/ubuntu precise partner
deb-src http://archive.canonical.com/ubuntu precise partner

##############################################################
##################### UNOFFICIAL  REPOS ######################
##############################################################

###### 3rd Party Binary Repos

#### Custom GIS repositories
deb http://ppa.launchpad.net/imincik/gis/ubuntu precise main
deb http://ppa.launchpad.net/imincik/qgis2/ubuntu precise main

#### Google Chrome Browser - http://www.google.com/linuxrepositories/
deb http://dl.google.com/linux/chrome/deb/ stable main

#### Google Earth - http://www.google.com/linuxrepositories/
deb http://dl.google.com/linux/earth/deb/ stable main
EOF
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6CD44B55 # add imincik PPA key
wget -q https://dl-ssl.google.com/linux/linux_signing_key.pub -O- | sudo apt-key add - # add Google repositories key

# use APT proxy on server if configured
if [ -n "${GISLAB_APT_HTTP_PROXY}" ]; then
	cat << EOF > /etc/apt/apt.conf.d/02proxy
Acquire::http { Proxy "$GISLAB_APT_HTTP_PROXY"; };
EOF
else
	rm -f /etc/apt/apt.conf.d/02proxy
fi

# hold kernel packages from upgrade to avoid a need to restart server after
# installation (Vagrant box could provide up-to-date kernel image)
# TODO: use more recent way of holding packages (apt-mark hold)
echo "linux-image-$(uname -r) hold" | dpkg --set-selections
echo "linux-generic-pae hold" | dpkg --set-selections
echo "linux-image-generic-pae hold" | dpkg --set-selections

echo "grub-pc hold" | dpkg --set-selections # hold also grub because of some issue

apt-get update
apt-get --assume-yes --force-yes upgrade
apt-get --assume-yes --force-yes --no-install-recommends install htop vim mc
apt-get --assume-yes --force-yes install postgresql postgis postgresql-9.1-postgis nfs-kernel-server
apt-get --assume-yes --force-yes --no-install-recommends install apache2 apache2-mpm-worker libapache2-mod-fcgid libapache2-mod-wsgi \
	python-virtualenv python-dateutil qgis-mapserver
apt-get --assume-yes --force-yes --no-install-recommends install ltsp-server-standalone openssh-server isc-dhcp-server tftpd-hpa




#
### DHCP ###
#
# adding Apparmor profile to enable including allowed MACs from /etc/ltsp/dhcpd-clients-allowed.conf
cat << EOF > /etc/apparmor.d/local/usr.sbin.dhcpd
/etc/ltsp/dhcpd-clients-allowed.conf lrw,
EOF
service apparmor restart

# creating empty MACs file
cat << EOF > /etc/ltsp/dhcpd-clients-allowed.conf
group {
}
EOF

# DHCP server configuration
cat << EOF > /etc/ltsp/dhcpd.conf
authoritative;

subnet 192.168.50.0 netmask 255.255.255.0 {
    option routers 192.168.50.5;

    pool {
        $GISLAB_UNKNOWN_MAC_POLICY unknown clients;
        range 192.168.50.100 192.168.50.250;
        option domain-name "gis.lab";
        option domain-name-servers $GISLAB_DNS_SERVERS;
        option broadcast-address 192.168.50.255;
        option subnet-mask 255.255.255.0;
        option root-path "/opt/ltsp/i386";
        if substring( option vendor-class-identifier, 0, 9 ) = "PXEClient" {
            filename "/ltsp/i386/pxelinux.0";
        } else {
            filename "/ltsp/i386/nbi.img";
        }
    }
}
EOF

if [ "$GISLAB_UNKNOWN_MAC_POLICY" == "deny" ]; # if unknown MACs are denied load known ones from included file
then
    cat << EOF >> /etc/ltsp/dhcpd.conf
include "/etc/ltsp/dhcpd-clients-allowed.conf";
EOF
fi

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
### NFS Share ###
#
mkdir -p /storage/repository    # readable for all, writable only for server superuser
mkdir -p /storage/share         # readable for all, writable for file owners
mkdir -p /storage/barrel        # readable and writable for all NFS users

chmod ugo+rwx /storage/barrel

cat << EOF > /etc/exports
/home                       *(rw,sync,no_subtree_check)
/storage/repository         *(ro,sync,no_subtree_check)
/storage/share              *(rw,sync,no_subtree_check)
/storage/barrel             *(rw,sync,no_subtree_check,all_squash,insecure)
EOF

cat << EOF > /etc/fstab
/storage  /mnt  none  bind  0  0
EOF
mount /mnt  # bind mount to keep the same paths on server as on client

service nfs-kernel-server restart




#
#### PROJECTIONS ###
#
# customize projections support
/bin/bash /vagrant/system/projections/*-libs.sh




#
#### PostgreSQL ###
#
# allow network connections and local connection without password
sed -i "s/^#listen_addresses.*/listen_addresses = '*'/" /etc/postgresql/9.1/main/postgresql.conf
sed -i "s/local.*all.*all.*peer/local  all  all  trust/" /etc/postgresql/9.1/main/pg_hba.conf
sed -i "s/host.*all.*all.*127.0.0.1\/32.*md5/host  all  all  0.0.0.0\/0  md5/" /etc/postgresql/9.1/main/pg_hba.conf

# set search path
sed -i "s/^#search_path.*/search_path = '\"\$user\",public'/" /etc/postgresql/9.1/main/postgresql.conf

service postgresql restart

# create labusers group
sudo su - postgres -c "createuser --no-superuser --no-createdb --no-createrole --no-login labusers"

# create template database
sudo su - postgres -c "createdb -E UTF8 -T template0 template_postgis"
sudo su - postgres -c "psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql"
sudo su - postgres -c "psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql"
sudo su - postgres -c "psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT ALL ON geography_columns TO PUBLIC;\""
sudo su - postgres -c "psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\""

# adding additional projections support
sudo su - postgres -c "psql -d template_postgis -f /vagrant/system/projections/*-postgis.sql"

sudo su - postgres -c "psql -d template_postgis -c \"VACUUM FULL;\""
sudo su - postgres -c "psql -d template_postgis -c \"VACUUM FREEZE;\""
sudo su - postgres -c "psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\""
sudo su - postgres -c "psql -d postgres -c \"UPDATE pg_database SET datallowconn='false' WHERE datname='template_postgis';\""

# create gislab database
sudo su - postgres -c "createdb -T template_postgis gislab"
sudo su - postgres -c "psql -c \"GRANT CONNECT ON DATABASE gislab TO labusers;\""




#
### DATA ###
#
cp -a /vagrant/data /storage/repository/



#
### QGIS MAPSERVER AND WMS VIEWER ###
#
mkdir -p /usr/local/python-virtualenvs
virtualenv --clear --system-site-packages /usr/local/python-virtualenvs/wms-viewer
source /usr/local/python-virtualenvs/wms-viewer/bin/activate
pip install OWSLib==0.8.2
pip install WebOb==1.2.3
pip install WSGIProxy==0.2.2
deactivate

cp -a /vagrant/system/wms-viewer /var/www

cat << EOF > /etc/apache2/sites-available/wms-viewer
<VirtualHost *:80>
  ServerAdmin webmaster@localhost
  ServerName webgis.gis.lab

  DocumentRoot /var/www/
  <Directory />
    Options FollowSymLinks
    AllowOverride None
  </Directory>
  <Directory /var/www/wms-viewer/>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

  Alias /static/ /var/www/wms-viewer/static/

  <Directory /var/www/wms-viewer/static/>
    Order deny,allow
    Allow from all
  </Directory>

  AddHandler wsgi-script .py
  WSGIDaemonProcess wms-viewer python-path=/var/www/wms-viewer:/usr/local/python-virtualenvs/wms-viewer/lib/python2.7/site-packages
  WSGIProcessGroup wms-viewer
  WSGIScriptAlias / /var/www/wms-viewer/wms-viewer.py

  ErrorLog /var/log/apache2/wms-viewer-error.log
  CustomLog /var/log/apache2/wms-viewer-access.log combined
</VirtualHost>
EOF

a2enmod wsgi
a2enmod rewrite
a2ensite wms-viewer
service apache2 reload




#
### LTSP ###
#
/vagrant/system/bin/gislab-build-client-image.sh # build LTSP client image
/vagrant/system/bin/gislab-clients-allowed.sh    # allow LTSP clients




#
### USERS ###
#
echo -e "\n[GIS.lab]: Creating GIS.lab users accounts ..."
for account in "${GISLAB_USER_ACCOUNTS_AUTO[@]}"
do
	/vagrant/system/bin/gislab-adduser.sh $account
done


echo -e "\n[GIS.lab]: Done. GIS.lab is installed and ready to use!"

# vim: set ts=4 sts=4 sw=4 noet:
