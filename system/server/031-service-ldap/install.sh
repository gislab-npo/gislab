#
###  LDAP DATABASE ###
#
# Install and configure authentication server.

# Logging: 
#   production: /var/log/ldap-error.log
#   debug:      /var/log/ldap-debug.log

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  gnutls-bin
  ldapscripts
  ldap-utils
  libnss-ldap
  pwgen
  python-ldap
  slapd
  ssl-cert
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# configure PAM
pam-auth-update --force
auth-client-config -t nss -p lac_ldap

# LDAP configuration file for pam_ldap and nsswitch
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/ldap/ldap-pam.conf /etc/ldap.conf
gislab_config_header_to_file /etc/ldap.conf

# LDAP configuration file for clients
# configure base DN and URI and disable certificates verification
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/ldap/ldap.conf /etc/ldap/ldap.conf
gislab_config_header_to_file /etc/ldap/ldap.conf

# nsswitch configuration
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/ldap/nsswitch.conf /etc/nsswitch.conf
gislab_config_header_to_file /etc/nsswitch.conf

# ldapscripts configuration
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/ldapscripts/ldapscripts.conf /etc/ldapscripts/ldapscripts.conf
gislab_config_header_to_file /etc/ldapscripts/ldapscripts.conf


### LOGGING ###
ldapmodify -Q -Y EXTERNAL -H ldapi:/// << EOL
dn: cn=config
changetype: modify
delete: olcLogLevel
EOL

if [ "$GISLAB_DEBUG_SERVICES" == "no" ]; then
	ldapmodify -Q -Y EXTERNAL -H ldapi:/// << EOL
dn: cn=config
changetype: modify
add: olcLogLevel
olcLogLevel: none
EOL
else
	ldapmodify -Q -Y EXTERNAL -H ldapi:/// << EOL
dn: cn=config
changetype: modify
add: olcLogLevel
olcLogLevel: stats
EOL
fi

if [ "$GISLAB_DEBUG_SERVICES" == "no" ]; then
cat << EOF >> /etc/rsyslog.d/50-default.conf
local4.* /var/log/ldap-error.log
EOF
else
cat << EOF >> /etc/rsyslog.d/50-default.conf
local4.* /var/log/ldap-debug.log
EOF
fi

# create default log file
touch /var/log/ldap-error.log
chmod 0640 /var/log/ldap-error.log
chown syslog:adm /var/log/ldap-error.log

# check logs with logcheck
echo "/var/log/ldap-error.log" >> /etc/logcheck/logcheck.logfiles

service rsyslog restart


### DO NOT CONTINUE ON UPGRADE ###
if [ -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then return; fi


# generate and set LDAP admin password
# generally we don't need to know it, but we can
# find it in '/etc/ldapscripts/ldapscripts.passwd'
LDAP_ADMIN_PASS=$(pwgen -s -N 1 10)
LDAP_ADMIN_PASS_HASH=$(slappasswd -s $LDAP_ADMIN_PASS -h {SSHA})

ldapmodify -Q -Y EXTERNAL -H ldapi:/// << EOL
dn: olcDatabase={1}hdb,cn=config
replace: olcRootPW
olcRootPW: $LDAP_ADMIN_PASS_HASH
EOL

echo -n "$LDAP_ADMIN_PASS" > /etc/ldapscripts/ldapscripts.passwd
chmod 0600 /etc/ldapscripts/ldapscripts.passwd


# secure LDAP with TLS
certtool --generate-privkey > /etc/ssl/private/cakey.pem

cat << EOL > /etc/ssl/ca.info
$(gislab_config_header)
cn = GIS.lab
ca
cert_signing_key
EOL

certtool --generate-self-signed \
--load-privkey /etc/ssl/private/cakey.pem \
--template /etc/ssl/ca.info \
--outfile /etc/ssl/certs/cacert.pem

certtool --generate-privkey \
--bits 1024 \
--outfile /etc/ssl/private/$(hostname)_slapd_key.pem

cat << EOL > /etc/ssl/$(hostname).info
$(gislab_config_header)
organization = GIS.lab
cn = $(hostname -f)
tls_www_server
encryption_key
signing_key
expiration_days = 3650
EOL

certtool --generate-certificate \
--load-privkey /etc/ssl/private/$(hostname)_slapd_key.pem \
--load-ca-certificate /etc/ssl/certs/cacert.pem \
--load-ca-privkey /etc/ssl/private/cakey.pem \
--template /etc/ssl/$(hostname).info \
--outfile /etc/ssl/certs/$(hostname)_slapd_cert.pem

ldapmodify -Q -Y EXTERNAL -H ldapi:/// << EOL
dn: cn=config
add: olcTLSCACertificateFile
olcTLSCACertificateFile: /etc/ssl/certs/cacert.pem
-
add: olcTLSCertificateFile
olcTLSCertificateFile: /etc/ssl/certs/$(hostname)_slapd_cert.pem
-
add: olcTLSCertificateKeyFile
olcTLSCertificateKeyFile: /etc/ssl/private/$(hostname)_slapd_key.pem
EOL

adduser openldap ssl-cert
chgrp ssl-cert /etc/ssl/private/$(hostname)_slapd_key.pem
chmod g+r /etc/ssl/private/$(hostname)_slapd_key.pem
chmod o-r /etc/ssl/private/$(hostname)_slapd_key.pem


# allow only encrypted connection
ldapmodify -Q -Y EXTERNAL -H ldapi:/// << EOL
dn: cn=config
changetype: modify
add: olcSecurity
olcSecurity: ssf=64
EOL


# add support for sudo
export DEBIAN_FRONTEND=noninteractive
export SUDO_FORCE_REMOVE=yes
apt-get -y install sudo-ldap
export SUDO_FORCE_REMOVE=no

ldapadd -Q -Y EXTERNAL -H ldapi:/// -f $GISLAB_INSTALL_CURRENT_ROOT/conf/ldap/sudo.schema

# add support for postfix
ldapadd -Q -Y EXTERNAL -H ldapi:/// -f $GISLAB_INSTALL_CURRENT_ROOT/conf/ldap/postfix.schema

# create indexes
ldapmodify -Q -Y EXTERNAL -H ldapi:/// << EOL
dn: olcDatabase={1}hdb,cn=config
add: olcDbIndex
olcDbIndex: default eq,sub
-
add: olcDbIndex
olcDbIndex: cn,sn,uid,mail,gn pres,eq,sub,subany
-
add: olcDbIndex
olcDbIndex: dc,ou eq
-
add: olcDbIndex
olcDbIndex: uidNumber,gidNumber eq
-
add: olcDbIndex
olcDbIndex: memberUid eq,pres,sub
-
add: olcDbIndex
olcDbIndex: displayName pres,sub,eq
-
add: olcDbIndex
olcDbIndex: uniqueMember pres,eq
-
add: olcDbIndex
olcDbIndex: sudoUser eq,sub,subany
-
add: olcDbIndex
olcDbIndex: mailacceptinggeneralid pres,eq
-
add: olcDbIndex
olcDbIndex: maildrop pres,eq
EOL


# create templates for users and groups
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/ldapscripts/adduser.template /etc/ldapscripts/adduser.template
cp $GISLAB_INSTALL_CURRENT_ROOT/conf/ldapscripts/addgroup.template /etc/ldapscripts/addgroup.template

# fix ldapscripts runtime script (https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=719295)
sed -i "s/^\[ -z \"\$USER\" \] && end_die 'Could not guess current user'$/\[ -n \"\$USER\" \] || USER=\$\(id -un 2>\/dev\/null\)/" /usr/share/ldapscripts/runtime

# restart service
service slapd restart


# create base GIS.lab LDAP structure
ldapadd -Z -w $LDAP_ADMIN_PASS -D "cn=admin,dc=gis,dc=lab" << EOL
dn: ou=People,dc=gis,dc=lab
objectClass: organizationalUnit
ou: people

dn: ou=Groups,dc=gis,dc=lab
objectClass: organizationalUnit
ou: groups

dn: ou=SUDOers,dc=gis,dc=lab
objectClass: top
objectClass: organizationalUnit
ou: SUDOers

dn: cn=defaults,ou=SUDOers,dc=gis,dc=lab
objectClass: top
objectClass: sudoRole
cn: defaults
description: Default sudoOption's go here
sudoOption: env_reset
sudoOption: secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$GISLAB_ROOT/system/bin:"

dn: cn=%labadmins,ou=SUDOers,dc=gis,dc=lab
objectClass: top
objectClass: sudoRole
cn: %labadmins
sudoUser: %labadmins
sudoHost: ALL
sudoCommand: ALL
sudoOption: !authenticate

dn: ou=MailAliases,dc=gis,dc=lab
objectClass: organizationalUnit
ou: mailaliases

dn: cn=root,ou=MailAliases,dc=gis,dc=lab
objectclass: top
objectClass: virtualaccount
cn: root
mailacceptinggeneralid: root
maildrop: $GISLAB_PROVISIONING_USER

dn: cn=labadmins,ou=Groups,dc=gis,dc=lab
objectClass: posixGroup
cn: labadmins
gidNumber: 3000
description: GIS.lab Admins Group

dn: cn=labusers,ou=Groups,dc=gis,dc=lab
objectClass: posixGroup
cn: labusers
gidNumber: 3001
description: GIS.lab Users Group
EOL

unset LDAP_ADMIN_PASS


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
