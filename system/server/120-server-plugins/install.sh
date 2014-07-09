#
### SERVER PLUGINS ###
#

for plugin in $GISLAB_ROOT/user/plugins/server/*.*; do
	gislab_print_info "Running server plugin '$(basename $plugin)'"
	GISLAB_INSTALL_ACTION=$GISLAB_INSTALL_ACTION $plugin
	echo "$(gislab_config_header)" >> /var/lib/gislab/server-plugin-$(basename $plugin).done
done


# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
