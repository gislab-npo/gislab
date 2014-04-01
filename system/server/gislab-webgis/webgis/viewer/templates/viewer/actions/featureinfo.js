
// Featureinfo Action

var identify_layer_combobox = new Ext.form.ComboBox({
	width: 150,
	mode: 'local',
	disabled: true,
	triggerAction: 'all',
	forceSelection: true,
	store: new Ext.data.JsonStore({
		data: {layers: []},
		storeId: 'search-layer-store',
		root: 'layers',
		fields: [{
			name: 'name',
			type: 'string'
		}]
	}),
	valueField: 'name',
	displayField: 'name',
	updateLayersList: function(layers_list) {
		var layers_options = ['All visible layers'].concat(layers_list);
		var store_data = [];
		Ext.each(layers_options, function(layername) {
			store_data.push({name: layername});
		});
		this.store.loadData({layers: store_data});
		if (layers_options.indexOf(this.getValue()) == -1) {
			this.setValue(layers_options[0]);
		}
	},
	listeners: {
		afterrender: function(combo) {
			var overlays_root = Ext.getCmp('layers-tree-panel').root;
			combo.updateLayersList(overlays_root.getVisibleLayers());
			overlays_root.on('layerchange', function(node, layer, visible_layers) {
				this.updateLayersList(visible_layers);
			}, combo);
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
	tooltip: 'Feature info',
	toggleHandler: function(button, toggled) {
		identify_layer_combobox.setDisabled(!toggled);
	}
})
mappanel.getTopToolbar().add(action, identify_layer_combobox);
