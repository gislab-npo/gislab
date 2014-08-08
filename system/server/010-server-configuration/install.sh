#
### BASIC SERVER CONFIGURATION ###
#
# Run basic server configuration.


# hosts
cat << EOF > /etc/hosts
$(gislab_config_header)
127.0.0.1 localhost
$GISLAB_SERVER_IP server.gis.lab server
EOF

cat << EOF > /etc/hostname
server
EOF
service hostname start
service rsyslog restart # restart syslog to read new hostname


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
$(gislab_config_header)
LANG="en_US.UTF-8"
LANGUAGE="en_US:en"
EOF


# add path to management scripts for sudo users. Configuration in 'vagrant-secure-path' is losing
# effect once sudo-ldap is installed
cat << EOF > /etc/sudoers.d/vagrant-secure-path
$(gislab_config_header)
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$GISLAB_ROOT/system/bin"
EOF
chmod 0440 /etc/sudoers.d/vagrant-secure-path


# save public SSH key
mkdir -p /etc/gislab/ssh
if [[ -n "$GISLAB_SSH_PRIVATE_KEY" && -n "$GISLAB_SSH_PUBLIC_KEY" ]]; then
	cp $GISLAB_ROOT/$GISLAB_SSH_PUBLIC_KEY /etc/gislab/ssh/gislab_ssh_public_key
else
	cp /home/$GISLAB_PROVISIONING_USER/.ssh/authorized_keys /etc/gislab/ssh/gislab_ssh_public_key
fi


### LOGGING ###
if [ "$GISLAB_DEBUG_SERVICES" == "no" ]; then
	sed -i '/^\$SystemLogRateLimitInterval 0$/d' /etc/rsyslog.conf
else
	# don't mute ldap when flooding
	echo "\$SystemLogRateLimitInterval 0" >> /etc/rsyslog.conf
fi
gislab_config_header_to_file /etc/rsyslog.conf

cat << EOF > /etc/rsyslog.d/50-default.conf
$(gislab_config_header)
auth,authpriv.*			/var/log/auth.log
*.*;auth,authpriv.none,mail.none,local4.none,local5.none,local7.none		-/var/log/syslog
kern.*					-/var/log/kern.log
news.crit				/var/log/news/news.crit
news.err				/var/log/news/news.err
news.notice				-/var/log/news/news.notice
*.emerg					:omusrmsg:*

daemon.*;mail.*;\\
	news.err;\\
	*.=debug;*.=info;\\
	*.=notice;*.=warn	|/dev/xconsole
EOF

service rsyslog restart


### DO NOT CONTINUE ON UPGRADE ###
if [ -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then return; fi
# set GIS.lab root directory variable
echo "GISLAB_ROOT=$GISLAB_ROOT" >> /etc/environment

# create empty local aliases table
echo > /etc/aliases
gislab_config_header_to_file /etc/aliases

# add admin scripts on PATH
echo "PATH="$PATH:$GISLAB_ROOT/system/bin"" >> /etc/profile
export PATH=$PATH:$GISLAB_ROOT/system/bin

# configure more informative server prompt
export PS1="\[$(tput bold)\]\u@\h.GIS.lab($GISLAB_UNIQUE_ID):\w\\$\[$(tput sgr0)\] "
echo "PS1='$PS1'" >> /home/$GISLAB_PROVISIONING_USER/.bashrc
echo "PS1='$PS1'" >> /etc/profile
echo "PS1='$PS1'" >> /etc/skel/.bashrc


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
