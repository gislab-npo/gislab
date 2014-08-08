#
### HAPROXY SERVER ###
#
# Install OWS server load balancer.


# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  haproxy
  unzip
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES

# install Serf
gislab_serf_install

# configure load balancer
if [ ! -f /var/lib/gislab/installation.done ]; then
	sed -i 's/^ENABLED=.*/ENABLED=1/' /etc/default/haproxy
fi


# TODO: always start server (after restart) with empty list of workers
cat << EOL > /etc/haproxy/haproxy.cfg
global
#   log 127.0.0.1 local0 warning
    maxconn 2000
    user haproxy
    group haproxy

defaults
    log global
    mode http
    option httplog
    option dontlognull
    option redispatch
    retries 3
    maxconn 2000
    timeout connect 5000
    timeout client 50000
    timeout server 50000

listen stats.gis.lab 0.0.0.0:1936
    mode http
    stats enable
    stats hide-version
    stats realm Haproxy\ Statistics
    stats uri /

listen ms.gis.lab 0.0.0.0:90
    mode http
    stats enable
    stats hide-version
    stats uri /haproxy?stats
    stats refresh 3s
    option httpchk GET /cgi-bin/qgis_mapserv.fcgi HTTP/1.1\r\nHost:\ ms.gis.lab
    balance static-rr
    fullconn 150
    maxconn 1000
    default-server error-limit 1 on-error fail-check fall 1 inter 10s fastinter 5s downinter 120s rise 2 maxconn 100 maxqueue 25 minconn 25 weight 128
    server localhost 127.0.0.1:91 maxconn 0

    # list of load balancer workers and clients in automaticaly managed by Serf below this line
EOL

service haproxy restart


# configure Serf
cp $GISLAB_INSTALL_CURRENT_ROOT/bin/serf-member-*.sh /usr/local/bin/
chmod +x /usr/local/bin/serf-member-*.sh

cp $GISLAB_INSTALL_CURRENT_ROOT/conf/serf/serf.conf /etc/init/serf.conf
service serf restart
