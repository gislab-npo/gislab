
// create permalink provider
var permalink_provider = new GeoExt.state.PermalinkProvider({encodeType: false});

// set it in the state manager
Ext.state.Manager.setProvider(permalink_provider);

var permalink = new Ext.Toolbar.TextItem({
	id: 'permalink',
	text: '<a target="_blank" href="#">Permalink</a>'
});
mappanel.getBottomToolbar().add(' ', '-', ' ', permalink);

// Register listeners for custom map state changes and generate events for permalink update
var fire_map_state_changed_event = function(obj) {
	permalink_provider.fireEvent('statechange', permalink_provider, "map", {});
};

var overlays_node = Ext.getCmp('layers-tree-panel').root;
if (overlays_node) {
	overlays_node.on('layerchange', fire_map_state_changed_event);
}

permalink_provider.on({
	statechange: function(provider, name, value) {
		var map = mappanel.map;

		var parameters = {
			DPI: OpenLayers.DOTS_PER_INCH,
			{% if project %}PROJECT: '{{ project }}',{% endif %}
			{% if scales %}SCALES: '{{ scales|join:"," }}',{% endif %}
			
		};
		var baselayers_combo = Ext.getCmp('base-layer-combo');
		if (baselayers_combo) {
			parameters.BASE = baselayers_combo.getEncodedLayersParam();
		}
		var overlays_root = Ext.getCmp('layers-tree-panel').root;
		if (overlays_root) {
			parameters.LAYERS = overlays_root.getEncodedLayersParam();
		}
		var extent_array = map.getExtent().toArray();
		for (var i = 0; i < 4; i++) {
			extent_array[i] = extent_array[i].toFixed(1);
		}
		parameters.EXTENT = extent_array.join(',');
		if (drawings_param) {
			parameters.DRAWINGS = drawings_param;
		}
		var link = [location.protocol, '//', location.host, location.pathname, '?'].join('');
		var qs = [];
		for (var param_name in parameters) {
			qs.push(encodeURIComponent(param_name) + "=" + encodeURIComponent(parameters[param_name]));
		}
		link += qs.join("&");
		permalink.setText('<a target="_blank" href="' + link + '">Permalink</a>');
	}
});
