#
### MAIL SERVER - POSTFIX ###
#

# disable logging to /var/log/syslog, /var/log/mail.err and to /var/log/mail.log
# and touch /var/log/mail-error.log to run logcheck successfuly
if [ ! -f /etc/gislab/033-service-mail.done ]; then
	sed -i 's|\(^.\+[^[:space:]]\)\([[:space:]]\+\)-/var/log/syslog$|\1,mail.none\2-/var/log/syslog|' /etc/rsyslog.d/50-default.conf
	sed -i '/^mail\.err[[:space:]]\+\/var\/log\/mail\.err$/d' /etc/rsyslog.d/50-default.conf
	sed -i '/^mail\.\*[[:space:]]\+-\/var\/log\/mail\.log$/d' /etc/rsyslog.d/50-default.conf
	touch /var/log/mail-error.log
	chown root:adm /var/log/mail-error.log
	chmod 0640 /var/log/mail-error.log
	rm -f /var/log/mail.log
	rm -f /var/log/mail.err
fi

sed -i '/^mail\.err[[:space:]]\+\/var\/log\/mail-error\.log$/d' /etc/rsyslog.d/50-default.conf
sed -i '/^mail\.\*[[:space:]]\+\/var\/log\/mail-debug\.log$/d' /etc/rsyslog.d/50-default.conf

if [ "$GISLAB_DEBUG_SERVICES" == "yes" ]; then
	# in debug mode log everything to /var/log/mail-debug.log
	echo "mail.* /var/log/mail-debug.log" >> /etc/rsyslog.d/50-default.conf
else
	# in non debug mode log only errors to /var/log/mail-error.log
	echo "mail.err /var/log/mail-error.log" >>/etc/rsyslog.d/50-default.conf
fi

service rsyslog restart

cat << EOL > /etc/postfix/main.cf
$(gislab_config_header)
smtpd_banner = \$myhostname ESMTP \$mail_name (Ubuntu)
biff = no
append_dot_mydomain = no
readme_directory = no
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls=yes
smtpd_tls_session_cache_database = btree:\${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:\${data_directory}/smtp_scache
myhostname = server.gis.lab
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
myorigin = /etc/mailname
mydestination = server.gis.lab, localhost.gis.lab, localhost
relayhost = 
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
inet_protocols = ipv4
virtual_alias_maps = regexp:/etc/postfix/virtual_regexp
message_size_limit = 52428800
EOL

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

service postfix restart


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
