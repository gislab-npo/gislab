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
sed -i 's/secure_path.*/secure_path="\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/vagrant\/system\/bin"/g' /etc/sudoers


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

# prevent Grub from waiting for manual input after a unsuccessful boot
cat << EOF >> /etc/default/grub
GRUB_RECORDFAIL_TIMEOUT=0
EOF
update-grub

apt-get update
apt-get --assume-yes --force-yes upgrade
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES




#
### BIND ###
#
cat << EOF > /etc/bind/named.conf.local
zone "gis.lab" {
    type master;
    file "/etc/bind/db.gis.lab";
};

zone "50.168.192.in-addr.arpa" {
    type master;
    file "/etc/bind/db.192";
};
EOF

cat << EOF > /etc/bind/db.gis.lab
\$TTL    604800
\$ORIGIN gis.lab.
@  3600  IN    SOA       ns.gis.lab. root.gis.lab. (
               2013112203     ; Serial
               604800         ; Refresh
               86400          ; Retry
               2419200        ; Expire
               604800         ; Negative Cache TTL
               )

         IN    NS       ns.gis.lab.

ns       IN    A        $GISLAB_NETWORK.5
ns1      IN    A        $GISLAB_NETWORK.5
ns1      IN    AAAA     ::1

server   IN    A        $GISLAB_NETWORK.5
web      IN    CNAME    server
webgis   IN    CNAME    server
balls    IN    CNAME    server
irc      IN    CNAME    server
EOF

cat << EOF > /etc/bind/db.192
\$TTL    604800
\$ORIGIN 50.168.192.IN-ADDR.ARPA.
@  3600  IN    SOA       ns.gis.lab. root.gis.lab. (
               2013112103     ; Serial
               604800         ; Refresh
               86400          ; Retry
               2419200        ; Expire
               604800         ; Negative Cache TTL
               )

         NS              ns.gis.lab.
5        IN    PTR       server.gis.lab.
EOF

service bind9 restart

# use our DNS server
cat << EOF >> /etc/resolvconf/resolv.conf.d/head
nameserver 127.0.0.1
EOF
resolvconf -u




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

subnet $GISLAB_NETWORK.0 netmask 255.255.255.0 {
    option routers $GISLAB_NETWORK.5;

    pool {
        $GISLAB_UNKNOWN_MAC_POLICY unknown clients;
        range $GISLAB_NETWORK.100 $GISLAB_NETWORK.250;
        option domain-name "gis.lab";
        option domain-name-servers $GISLAB_NETWORK.5, $GISLAB_DNS_SERVERS;
        option broadcast-address $GISLAB_NETWORK.255;
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

service isc-dhcp-server restart




#
### IP FORWARDING ###
#
# set IP forwarding for client machines and call it from rc.local to run it after server restart
cat << EOF > /usr/local/bin/enable-ip-forward
#!/bin/bash

sysctl -w net.ipv4.ip_forward=1
iptables --table nat --append POSTROUTING --jump MASQUERADE --source $GISLAB_NETWORK.0/24
EOF

chmod +x /usr/local/bin/enable-ip-forward
/usr/local/bin/enable-ip-forward

sed -i "s/exit 0//" /etc/rc.local
echo "/usr/local/bin/enable-ip-forward" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local




#
### NFS SHARE ###
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

sed -i "s/^# Domain.*/Domain = gis.lab/" /etc/idmapd.conf

cat << EOF > /etc/fstab
/storage  /mnt  none  bind  0  0
EOF
mount /mnt  # bind mount to keep the same paths on server as on client

service nfs-kernel-server restart
service idmapd restart




#
### IRC ###
#
cat << EOF > /etc/ircd-hybrid/ircd.conf
serverinfo {
    name = "irc.gis.lab";
    description = "GIS.lab IRC server";
    network_name = "GIS.lab";
    network_desc = "GIS.lab";
    hub = yes;
    max_clients = 512;
};

admin {
    name = "GIS.lab Administrator";
    description = "GIS.lab Administrator";
    email = "root@server.gis.lab";
};
EOF

cat /vagrant/system/server/ircd/ircd.conf >> /etc/ircd-hybrid/ircd.conf # append rest of config

cat << EOF > /etc/ircd-hybrid/ircd.motd
Welcome to GIS.lab IRC server !
EOF

service ircd-hybrid restart




#
#### PROJECTIONS ###
#
# customize projections support
/bin/bash /vagrant/user/projections/*-libs.sh




#
#### POSTGRESQL ###
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
sudo su - postgres -c "psql -d template_postgis -f /vagrant/user/projections/*-postgis.sql"

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
cp -a /vagrant/user/data /storage/repository/




#
### WEBGIS ###
#
cp -a /vagrant/system/server/webgis /var/www

mkdir -p /usr/local/python-virtualenvs
virtualenv --clear --system-site-packages /usr/local/python-virtualenvs/webgis
source /usr/local/python-virtualenvs/webgis/bin/activate
pip install -r /var/www/webgis/requirements.txt
deactivate

cat << EOF > /etc/apache2/sites-available/webgis
<VirtualHost *:80>
  ServerAdmin webmaster@localhost
  ServerName web.gis.lab
  ServerAlias webgis.gis.lab

  DocumentRoot /var/www/
  <Directory />
    Options FollowSymLinks
    AllowOverride None
  </Directory>
  <Directory /var/www/webgis/>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

  Alias /static/ /var/www/webgis/static/

  <Directory /var/www/webgis/static/>
    Order deny,allow
    Allow from all
  </Directory>

  AddHandler wsgi-script .py
  WSGIDaemonProcess webgis python-path=/var/www/webgis:/usr/local/python-virtualenvs/webgis/lib/python2.7/site-packages
  WSGIProcessGroup webgis
  WSGIScriptAlias / /var/www/webgis/webgis.py

  ErrorLog /var/log/apache2/webgis-error.log
  CustomLog /var/log/apache2/webgis-access.log combined
</VirtualHost>
EOF

a2enmod wsgi
a2enmod rewrite
a2ensite webgis
service apache2 reload




#
### BALLS ###
#

BALLS_PASSWORD=$(pwgen -1 -n 8)
sudo su - postgres -c "createdb -E UTF8 -T template0 balls"
sudo su - postgres -c "createuser --no-superuser --no-createdb --no-createrole balls" # PostgreSQL account
sudo su - postgres -c "psql -c \"ALTER ROLE balls WITH PASSWORD '${BALLS_PASSWORD}';\""

virtualenv --clear --system-site-packages /usr/local/python-virtualenvs/balls
source /usr/local/python-virtualenvs/balls/bin/activate
pip install -r /vagrant/system/server/gislab-balls/requirements.txt
python /vagrant/system/server/gislab-balls/setup.py install

mkdir -p /var/www/balls
django-admin.py startproject --template=/vagrant/system/server/gislab-balls/balls/conf/project_template/ djproject /var/www/balls

cat << EOF >> /var/www/balls/djproject/settings.py
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'balls',
		'USER': 'balls',
		'PASSWORD': '$BALLS_PASSWORD',
		'HOST': '',
		'PORT': '',
	}
}
EOF

python /var/www/balls/manage.py syncdb --noinput
deactivate

cp -a /vagrant/system/server/gislab-balls/conf/balls.apache /etc/apache2/sites-available/balls

a2ensite balls
service apache2 reload




#
### CLIENT INSTALLATION ###
#
/vagrant/system/bin/gislab-install-client # install client image
/vagrant/system/bin/gislab-clients-allowed # allow client MACs




#
### SERVER PLUGINS ###
#
for plugin in /vagrant/user/plugins/server/*.*; do
	$plugin
done




#
### USERS ###
#
# remove default 'ubuntu' user account if exists
if id -u ubuntu > /dev/null 2>&1; then deluser ubuntu --remove-home ; fi

echo "vagrant:$(pwgen -1 -n 12)" | chpasswd # set strong password for vagrant user


echo -e "\n[GIS.lab]: Creating GIS.lab users accounts ..."
for account in "${GISLAB_USER_ACCOUNTS_AUTO[@]}"
do
	/vagrant/system/bin/gislab-adduser -p lab $account
done


echo -e "\n[GIS.lab]: Done. GIS.lab is installed and ready to use!"

# vim: set ts=4 sts=4 sw=4 noet:
