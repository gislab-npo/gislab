{% load i18n %}
// Featureinfo Action

var identify_layer_combobox = new Ext.form.ComboBox({
	width: 150,
	mode: 'local',
	disabled: true,
	editable: false,
	tooltip: '{% trans "Layer" %}',
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
		var layers_options = ['{% trans "All visible layers" %}'].concat(layers_list);
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
			Ext.QuickTips.register({ target: combo.getEl(), text: combo.tooltip });
			// get list of queryable layers
			var queryable_layers = [];
			var layers_meta = {};
			Ext.getCmp('layers-tree-panel').root.cascade(function(node) {
				if (node.isLeaf() && node.attributes.config.queryable) {
					queryable_layers.push(node.attributes.text);
					layers_meta[node.attributes.text] = node.attributes.config
				}
			});
			combo.queryableLayers = queryable_layers;
			var featureinfo_panel = Ext.getCmp('featureinfo-panel');
			featureinfo_panel.setLayersMetadata(layers_meta);

			var on_visible_layers_changed = function(node, layer, visible_layers) {
				var layers_list = [];
				Ext.each(visible_layers, function(layer_name) {
					if (this.queryableLayers.indexOf(layer_name) != -1) {
						layers_list.push(layer_name);
					}
				}, this);
				this.updateLayersList(layers_list);
			}.bind(combo);

			var overlays_root = Ext.getCmp('layers-tree-panel').root;
			on_visible_layers_changed(overlays_root, overlays_root.layer, overlays_root.getVisibleLayers());
			overlays_root.on('layerchange', on_visible_layers_changed, combo);
		}
	}
});

/*
  We have to customize OpenLayers.Control.WMSGetFeatureInfo to make work with both
  OpenLayers.Layers.WMS and OpenLayers.Layers.TMS layer types and to control LAYERS
  parameter in GetFeatureInfo:

   * set WMSGetFeatureInfo's url that will differ from any url of map WMS layers or simply any invalid value. Thish will
     prevent WMSGetFeatureInfo control to perform automatic GetFeatureInfo requests.
   * handle 'beforegetfeatureinfo' events and manually perform GetFeatureInfo requests with proper LAYERS value.
*/
ctrl = new OpenLayers.Control.WMSGetFeatureInfo({
	url: 'null',
	autoActivate: false,
	infoFormat: 'application/vnd.ogc.gml',
	maxFeatures: 10,
	featureinfo_layer: new OpenLayers.Layer.WMS(
		'WmsOverlaysLayer',
		'{{ ows_url }}',
		{},
		{ projection: config.projection}
	),
	eventListeners: {
		beforegetfeatureinfo: function(event) {
			if (identify_layer_combobox.selectedIndex > 0) {
				this.featureinfo_layer.params.LAYERS = [identify_layer_combobox.getValue()];
			} else {
				this.featureinfo_layer.params.LAYERS = Ext.getCmp('layers-tree-panel').root.getVisibleLayers();
			}
			var wms_options = this.buildWMSOptions(this.featureinfo_layer.url, [this.featureinfo_layer], event.xy);
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
	tooltip: '{% trans "Identify features by mouse click" %}',
	toggleHandler: function(action, toggled) {
		identify_layer_combobox.setDisabled(!toggled);
	}
})
mappanel.getTopToolbar().add(action, ' ', identify_layer_combobox);
