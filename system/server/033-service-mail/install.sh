#
### MAIL SERVER - POSTFIX ###
#

# Logging: 
#   production: /var/log/mail-error.log
#   debug:      /var/log/mail-debug.log


# main configuration file
cp /vagrant/system/server/033-service-mail/conf/postfix/main.cf /etc/postfix/main.cf
gislab_config_header_to_file /etc/postfix/main.cf

# send admin email by default to provisioning user
echo "/.+@.+/ $GISLAB_PROVISIONING_USER" > /etc/postfix/virtual_regexp

rm -f /etc/postfix/sasl_passwd /etc/postfix/sasl_passwd.db

if [ -n "$GISLAB_SERVER_EMAIL_RELAY_LOGIN" -a -n "$GISLAB_SERVER_EMAIL_RELAY_PASSWORD" -a -n "$GISLAB_SERVER_EMAIL_RELAY_SERVER" ]; then
	sed -i "s/^relayhost =.*/relayhost = [$GISLAB_SERVER_EMAIL_RELAY_SERVER]:587/" /etc/postfix/main.cf
	echo "smtp_tls_security_level = encrypt" >>  /etc/postfix/main.cf
	echo "smtp_sasl_security_options = noanonymous" >> /etc/postfix/main.cf
	echo "smtp_sasl_auth_enable = yes" >>  /etc/postfix/main.cf
	echo "smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd" >> /etc/postfix/main.cf
	echo "[$GISLAB_SERVER_EMAIL_RELAY_SERVER]:587 $GISLAB_SERVER_EMAIL_RELAY_LOGIN:$GISLAB_SERVER_EMAIL_RELAY_PASSWORD" > /etc/postfix/sasl_passwd
	chmod 0600 /etc/postfix/sasl_passwd
	postmap /etc/postfix/sasl_passwd

	# send system emails to all users in labadmins group
	ldapsearch_cmd="ldapsearch -Q -LLL -Y EXTERNAL -H ldapi:///"
	for user in $($ldapsearch_cmd -b "cn=labadmins,ou=Groups,dc=gis,dc=lab" memberUid | awk '/^memberUid:/ { print $2 }'); do
		for mail in $($ldapsearch_cmd -b "ou=People,dc=gis,dc=lab" "uid=$user" mail | awk '/^mail: / { print $2 }'); do
			sed -i "s/\(.*\)/\1, $mail/" /etc/postfix/virtual_regexp
		done
	done
fi

service postfix restart


### LOGGING ###
if [ "$GISLAB_DEBUG_SERVICES" == "no" ]; then
cat << EOF >> /etc/rsyslog.d/50-default.conf
mail.err /var/log/mail-error.log
EOF
else
cat << EOF >> /etc/rsyslog.d/50-default.conf
mail.* /var/log/mail-debug.log
EOF
fi

# create default log file
touch /var/log/mail-error.log
chmod 0640 /var/log/mail-error.log
chown syslog:adm /var/log/mail-error.log

# remove system default log files
rm -f /var/log/mail.log
rm -f /var/log/mail.err

service rsyslog restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
