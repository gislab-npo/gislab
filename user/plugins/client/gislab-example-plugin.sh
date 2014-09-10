# Example GIS.lab client plugin


echo "Running an example GIS.lab client plugin."
case "$MODE" in
	commandline)
		add_option "example-option" "`eval_gettext "example option"`" "advanced" "true"
	;;

	configure)
		if [ -n "$option_example_option_value" ]; then
			EXAMPLE_OPTION="$(echo $option_example_option_value | tr ',' ' ')"
		fi
	;;

	before-install)
		echo "Performing before-install part of GIS.lab client installation."
		echo "Example option: $EXAMPLE_OPTION"
	;;

	install)
		echo "Performing install part of GIS.lab client installation."
	;;

	after-install)
		echo "Performing after-install part of GIS.lab client installation."
	;;

	finalization)
		echo "Performing finalization part of GIS.lab client installation."
	;;
esac

# vim: set ts=4 sts=4 sw=4 noet:
