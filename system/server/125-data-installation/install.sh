#
### DATA ###
#

### SKIP ON UPGRADE ###
if [ -f "/var/lib/gislab/$GISLAB_INSTALL_CURRENT_SERVICE.done" ]; then return; fi

cp -a /$GISLAB_ROOT/user/data /storage/repository/
chown -R :labadmins /storage/repository/*


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
