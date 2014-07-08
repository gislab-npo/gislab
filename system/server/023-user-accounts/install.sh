#
### USER ACCOUNTS ###
#

# packages installation
GISLAB_SERVER_INSTALL_PACKAGES="
  pwgen
"
apt-get --assume-yes --force-yes --no-install-recommends install $GISLAB_SERVER_INSTALL_PACKAGES


# Some server images are using 'vagrant' account (VirtualBox) for provisioning, some 
# of them are using 'ubuntu' account (AWS). Remove those which we do not use.
for account in vagrant ubuntu; do
	if id -u $account > /dev/null 2>&1; then
		if [ "$account" != "$GISLAB_PROVISIONING_USER" ]; then
			deluser --remove-home $account
		fi
	fi
done

# set strong password and file access permissions for provisioning account
echo "$GISLAB_PROVISIONING_USER:$(pwgen -1 -n 24)" | chpasswd
chmod 700 /home/$GISLAB_PROVISIONING_USER
chmod 700 /home/$GISLAB_PROVISIONING_USER/.ssh

# set public SSH key for provisioning account
cp /etc/gislab/ssh/gislab_ssh_public_key /home/$GISLAB_PROVISIONING_USER/.ssh/authorized_keys


### BACKUP ###
mkdir -p /etc/cron.d.bin
cp $GISLAB_INSTALL_CURRENT_ROOT/bin/gislab-backup-users.sh /etc/cron.d.bin
cat << EOL > /etc/cron.d/gislab-backup-users
$(gislab_config_header)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/vagrant/system/bin
MAILTO=root

0 2	* * *  root  nice /etc/cron.d.bin/gislab-backup-users.sh > /dev/null
EOL


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
