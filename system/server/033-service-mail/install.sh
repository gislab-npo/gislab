#
### MAIL SERVER - POSTFIX ###
#

# write main configuration file
cp /vagrant/system/server/033-service-mail/conf/postfix/main.cf /etc/postfix/main.cf
gislab_config_header_to_file /etc/postfix/main.cf

# send admin email to vagrant if exists, else send it to ubuntu or root
if id vagrant >/dev/null 2>&1; then
	default_admin_mail=vagrant
elif id ubuntu >/dev/null 2>&1; then
	default_admin_mail=ubuntu
else
	default_admin_mail=root
fi

echo "/.+@.+/ $default_admin_mail" > /etc/postfix/virtual_regexp

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

# remove system default log files
rm -f /var/log/mail.log
rm -f /var/log/mail.err

# touch log file and set appropriate mode and ownership
touch /var/log/mail-error.log
chmod 0640 /var/log/mail-error.log
chown syslog:adm /var/log/mail-error.log

# restart services
service postfix restart
service rsyslog restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
