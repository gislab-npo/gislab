#
### DNS SERVER - BIND ###
#

# Logging: 
#   production: -
#   debug:      /var/log/named/named-debug.log


GISLAB_NETWORK_REVERSE=$(echo $GISLAB_SERVER_IP | awk -F "." '{ print $3 "." $2 "." $1 }')

# main configuration
# use IPv4 only
cat << EOF > /etc/default/bind9
$(gislab_config_header)
RESOLVCONF=no
OPTIONS="-4 -u bind"
EOF

cat << EOF > /etc/bind/named.conf
$(gislab_config_header)

include "/etc/bind/named.conf.options";
include "/etc/bind/named.conf.local";
include "/etc/bind/named.conf.default-zones";

logging {
	channel default_syslog {
		null;
	};

	channel default_debug {
		null;
	};

	channel debug_log {
		syslog local5;
		severity info;
		print-time yes;
		print-severity yes;
		print-category yes;
	};

	category default {
		debug_log;
	};

	category unmatched {
		null;
	};
EOF

if [ "$GISLAB_DEBUG_SERVICES" == "yes" ]; then
	cat << EOF >> /etc/bind/named.conf

	category queries {
		debug_log;
	};
EOF
	echo "local5.* /var/log/named-debug.log" >> /etc/rsyslog.d/50-default.conf
else
	echo "local5.* /var/log/named-error.log" >> /etc/rsyslog.d/50-default.conf
fi

echo "};" >> /etc/bind/named.conf

# gis.lab zone
cat << EOF > /etc/bind/named.conf.local
$(gislab_config_header)

zone "gis.lab" {
    type master;
    file "/etc/bind/db.gis.lab";
};

zone "$GISLAB_NETWORK_REVERSE.in-addr.arpa" {
    type master;
    file "/etc/bind/db.192";
};
EOF

cat << EOF > /etc/bind/db.gis.lab
$(gislab_config_header ";")

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

ns       IN    A        $GISLAB_SERVER_IP
ns1      IN    A        $GISLAB_SERVER_IP
ns1      IN    AAAA     ::1

server   IN    A        $GISLAB_SERVER_IP
boot     IN    CNAME    server
db       IN    CNAME    server
ms       IN    CNAME    server
web      IN    CNAME    server
chat     IN    CNAME    server
stats    IN    CNAME    server
EOF

cat << EOF > /etc/bind/db.192
$(gislab_config_header ";")

\$TTL    604800
\$ORIGIN $GISLAB_NETWORK_REVERSE.IN-ADDR.ARPA.
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

# create default log file
touch /var/log/named-error.log
chmod 0640 /var/log/named-error.log
chown syslog:adm /var/log/named-error.log

service rsyslog restart
service bind9 restart


# use our DNS server
cat << EOF > /etc/resolvconf/resolv.conf.d/head
$(gislab_config_header)
nameserver 127.0.0.1
EOF
resolvconf -u


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
