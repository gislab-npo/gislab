
// Featureinfo Action
var layers_store_data = {
	layers: [
		{ name: 'All visible layers' },
		{% for layer in layers %}
		{ name: '{{ layer.name }}' },
		{% endfor %}
	]
};

var identify_layer_combobox = new Ext.form.ComboBox({
	width: 150,
	mode: 'local',
	triggerAction: 'all',
	forceSelection: true,
	store: new Ext.data.JsonStore({
		data: layers_store_data,
		storeId: 'search-layer-store',
		root: 'layers',
		fields: [{
			name: 'name',
			type: 'string'
		}]
	}),
	valueField: 'name',
	displayField: 'name',
	listeners: {
		afterrender: function(combo) {
			if (combo.getStore().getCount() > 0) {
				var recordSelected = combo.getStore().getAt(0);
				combo.setValue(recordSelected.get('name'));
			}
		}
	}
});

ctrl = new OpenLayers.Control.WMSGetFeatureInfo({
	url: '{{ getfeatureinfo_url }}',
	autoActivate: false,
	infoFormat: 'application/vnd.ogc.gml',
	maxFeatures: 10,
	eventListeners: {
		beforegetfeatureinfo: function(event) {
			// because we provided 'url' parameter that will not match url of any layer,
			// GetFeatureInfo request will not be performed automatically, so we have to
			// create it manualy with given 'url'.
			var visible_layers = overlays_group_layer.params.LAYERS; // save LAYERS parameter value
			if (identify_layer_combobox.selectedIndex > 0) {
				this.queryVisible = false;
				overlays_group_layer.params.LAYERS = [identify_layer_combobox.getValue()];
			} else {
				this.queryVisible = true;
			}
			var wms_options = this.buildWMSOptions(this.url, [overlays_group_layer], event.xy);
			overlays_group_layer.params.LAYERS = visible_layers; // restore LAYERS parameter value
			var request = OpenLayers.Request.GET(wms_options);
		},
		getfeatureinfo: function(e) {
			Ext.getCmp('featureinfo-panel').showFeatures(e.features);
		}
	}
})
action = new GeoExt.Action({
	control: ctrl,
	map: mappanel.map,
	cls: 'x-btn-icon',
	iconCls: 'featureinfo-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	group: 'tools',
	tooltip: 'Feature info'
})
mappanel.getTopToolbar().add(identify_layer_combobox, '-', action);
