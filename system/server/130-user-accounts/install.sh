#
### USER ACCOUNTS ###
#

# Some Vagrant boxes are using 'vagrant' account (VirtualBox) for provisioning, some 
# of them are using 'ubuntu' account (AWS).

# set strong password and file access permissions for provisioning accounts
for account in vagrant ubuntu; do
	if id -u $account > /dev/null 2>&1; then
		echo "$account:$(pwgen -1 -n 24)" | chpasswd
		chmod 700 /home/$account
		chmod 700 /home/$account/.ssh
	fi
done

# replace Vagrant insecure SSH key
if [[ -n "$GISLAB_SSH_PRIVATE_KEY" && -n "$GISLAB_SSH_PUBLIC_KEY" ]]; then
	for account in vagrant ubuntu; do
		if id -u $account > /dev/null 2>&1; then
			cat /vagrant/$GISLAB_SSH_PUBLIC_KEY > /home/$account/.ssh/authorized_keys
		fi
	done
fi


### BACKUP ###
mkdir -p /etc/cron.d.bin
cp /vagrant/system/server/130-user-accounts/bin/gislab-backup-users.sh /etc/cron.d.bin
cat << EOL > /etc/cron.d/gislab-backup-users
$(gislab_config_header)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/vagrant/system/bin
MAILTO=root

0 2	* * *  root  nice /etc/cron.d.bin/gislab-backup-users.sh > /dev/null
EOL


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
