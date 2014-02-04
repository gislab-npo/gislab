
// Featureinfo Action
ctrl = new OpenLayers.Control.WMSGetFeatureInfo({
	url: '{{ getfeatureinfo_url }}',
	autoActivate: false,
	infoFormat: 'application/vnd.ogc.gml',
	maxFeatures: 10,
	queryVisible: true,
	eventListeners: {
		beforegetfeatureinfo: function(event) {
			// because we provided 'url' parameter that will not match url of any layer,
			// GetFeatureInfo request will not be performed automatically, so we have to
			// create it manualy with given 'url'.
			var wms_options = this.buildWMSOptions(this.url, [overlays_group_layer], event.xy);
			var request = OpenLayers.Request.GET(wms_options);
		},
		getfeatureinfo: function(e) {
			featureinfo_panel.showFeatures(e.features);
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
mappanel.getTopToolbar().add('-', action);
