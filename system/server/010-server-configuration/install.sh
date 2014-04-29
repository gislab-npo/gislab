#
### BASIC SERVER CONFIGURATION ###
#

# Read server IP from running server and update GISLAB_NETWORK. This is done because some 
# cloud providers like AWS ignore IP address given by Vagrantfile and set it by their own.
GISLAB_SERVER_IP=$(hostname  -I | awk -F" " '{print $NF}')
GISLAB_NETWORK=$(echo $GISLAB_SERVER_IP | awk -F "." '{ print $1 "." $2 "." $3 }')


# replace Vagrant insecure SSH key
if [[ -n "$GISLAB_SSH_PRIVATE_KEY" && -n "$GISLAB_SSH_PUBLIC_KEY" ]]; then
	if id -u vagrant > /dev/null 2>&1; then
		cat /vagrant/$GISLAB_SSH_PUBLIC_KEY > /home/vagrant/.ssh/authorized_keys
	fi
	if id -u ubuntu > /dev/null 2>&1; then
		cat /vagrant/$GISLAB_SSH_PUBLIC_KEY > /home/ubuntu/.ssh/authorized_keys
	fi
fi


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
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/vagrant/system/bin"
EOF
chmod 0440 /etc/sudoers.d/vagrant-secure-path

# do not continue on upgrade
if [ -f "/etc/gislab/010-server-configuration.done" ]; then return; fi

# add admin scripts on PATH
echo "PATH="$PATH:/vagrant/system/bin"" >> /etc/profile
export PATH=$PATH:/vagrant/system/bin

# configure more informative server prompt
export PS1="\[$(tput bold)\]\u@server.gis.lab($GISLAB_UNIQUE_ID):\w\\$\[$(tput sgr0)\] "
if id -u vagrant > /dev/null 2>&1; then echo "PS1='$PS1'" > /home/vagrant/.bashrc; fi
if id -u ubuntu > /dev/null 2>&1; then echo "PS1='$PS1'" > /home/ubuntu/.bashrc; fi
echo "PS1='$PS1'" >> /etc/profile
echo "PS1='$PS1'" >> /etc/skel/.bashrc


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
