#
### PROVIDER CUSTOMIZATIONS - AWS ###
#
# Amazon AWS provider customizations.


# detect AWS instance properties
aws_meta_url="http://169.254.169.254/latest/meta-data"
GISLAB_SERVER_AWS_INSTANCE_ID=$(curl $aws_meta_url/instance-id)
GISLAB_SERVER_AWS_LOCAL_IP=$(curl $aws_meta_url/local-ipv4)
GISLAB_SERVER_AWS_PUBLIC_IP=$(curl $aws_meta_url/public-ipv4)
GISLAB_SERVER_AWS_PUBLIC_HOSTNAME=$(curl $aws_meta_url/public-hostname)

# configure GIS.lab Web with AWS instance values
sed -i "s/server_name web.gis.lab;/server_name web.gis.lab $GISLAB_SERVER_AWS_PUBLIC_HOSTNAME;/" /etc/nginx/sites-available/webgis
sed -i "/ALLOWED_HOSTS/aALLOWED_HOSTS += ['$GISLAB_SERVER_AWS_PUBLIC_HOSTNAME']" /var/www/webgis/djproject/settings.py
service apache2 reload

# do not continue on upgrade
if [ -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then return; fi

# if instance contains ephemeral0 disk use it for database storage
if [ -b /dev/xvdb ]; then
	umount /dev/xvdb || true
	mkfs.ext4 /dev/xvdb
	sleep 2
	
	sed -i "/xvdb/d" /etc/fstab
	echo "/dev/xvdb  /var/lib/postgresql  ext4  noatime,nodiratime,nobootwait,comment=cloudconfig 0 2" >> /etc/fstab

	service postgresql stop
	sleep 2
	mv /var/lib/postgresql /var/lib/postgresql.old
	mkdir -p /var/lib/postgresql
	mount /dev/xvdb /var/lib/postgresql
	chown postgres:postgres /var/lib/postgresql
	mv /var/lib/postgresql.old/* /var/lib/postgresql/
	rm -rf /var/lib/postgresql.old
	service postgresql start
	
fi

# if instance contains ephemeral1 disk use it for files storage
if [ -b /dev/xvdc ]; then
	umount /dev/xvdc || true
	mkfs.ext4 /dev/xvdc
	sleep 2

	sed -i "/xvdc/d" /etc/fstab
	echo "/dev/xvdc  /storage  ext4  noatime,nodiratime,nobootwait,comment=cloudconfig 0 2" >> /etc/fstab

	service nfs-kernel-server stop
	sleep 2
	umount /mnt # /storage bind mount
	mv /storage /storage.old
	mkdir /storage
	mount /dev/xvdc /storage
	mv /storage.old/* /storage/
	rm -rf /storage.old
	mount /mnt # /storage bind mount
	service nfs-kernel-server start
fi

# prevent further star of DHCP server which does not make sense in AWS (even target device eth1 does not exist)
echo "manual" >> /etc/init/isc-dhcp-server.override


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
