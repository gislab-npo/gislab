#
### USER ACCOUNTS ###
#

# Some Vagrant boxes are using 'vagrant' account for provisioning, some of them are
# using 'ubuntu' account. Set strong password for these accounts.
# Test which account exists and set strong password.
if id -u vagrant > /dev/null 2>&1; then echo "vagrant:$(pwgen -1 -n 24)" | chpasswd; fi
if id -u ubuntu > /dev/null 2>&1; then echo "ubuntu:$(pwgen -1 -n 24)" | chpasswd; fi


# activate backup
mkdir -p /etc/cron.d.bin
cp /vagrant/system/server/130-user-accounts/bin/gislab-backup-users.sh /etc/cron.d.bin
cat << EOL > /etc/cron.d/gislab-backup-users
$(gislab_config_header)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/vagrant/system/bin
MAILTO=root

0 2	* * *  root  nice /etc/cron.d.bin/gislab-backup-users.sh > /dev/null
EOL


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
