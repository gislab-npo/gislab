
var draw_controls = [
	// Draw points control
	{
		title: 'Points',
		iconCls: 'draw-point-icon',
		control: new OpenLayers.Control.DrawFeature(
			points_layer,
			OpenLayers.Handler.Point,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						label: ''
					};
					// update feature on map
					points_layer.drawFeature(feature);
				}
			}
		)
	},

	// Draw lines control
	{
		title: 'Lines',
		iconCls: 'draw-line-icon',
		control: new OpenLayers.Control.DrawFeature(
			lines_layer,
			OpenLayers.Handler.Path,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						label: ''
					};
					// update feature on map
					lines_layer.drawFeature(feature);
				}
			}
		)
	},

	// Draw polygons control
	{
		title: 'Polygons',
		iconCls: 'draw-polygon-icon',
		control: new OpenLayers.Control.DrawFeature(
			polygons_layer,
			OpenLayers.Handler.Polygon,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						label: ''
					};
					// update feature on map
					polygons_layer.drawFeature(feature);
				}
			}
		)
	}
];

action = new WebGIS.DrawAction({
	controls: draw_controls,
	map: mappanel.map,
	cls: 'x-btn-icon',
	iconCls: 'draw-line-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	tooltip: 'Draw geometry',
	snapping: true,
	toggleHandler: function(action, toggled) {
		action.baseAction.toggleHandler(action, toggled);
	},
	saveHandler: function(drawAction, title, features) {
		if (features.length > 0) {
			var geojson = new OpenLayers.Format.GeoJSON().write(features, true);
			// add projection info
			if (drawAction.map.projection) {
				var geojson_obj = JSON.parse(geojson);
				geojson_obj.crs = new OpenLayers.Format.GeoJSON().createCRSObject(features[0]);
				geojson_obj.metadata = {
					title: title,
					timestamp: new Date()
				}
				geojson = JSON.stringify(geojson_obj, null, '    ');
			}
			Ext.Ajax.request({
				method: 'POST',
				url: '{% url "webgis.storage.views.ball" %}',
				jsonData: geojson,
				headers: { 'Content-Type': 'application/geojson; charset=utf-8' },
				success: function(response) {
					drawings_param = response.responseText;
					Ext.state.Manager.set("map", {drawings: [response.responseText]});
					Ext.getCmp('geojson-links').setLinks([{
						name: title,
						hyperlink_text: response.responseText,
						href: Ext.urlAppend('{% url "webgis.storage.views.ball" %}', Ext.urlEncode({ID: response.responseText})),
					}]);

					// Add record into saving history
					var permalink_url = Ext.get('permalink').dom.children[0].href;
					var drawing_info = String.format('points: {0} lines: {1} polygons: {2}', points_layer.features.length, lines_layer.features.length, polygons_layer.features.length);
					var data = [[title, new Date(), String.format('<a target="_blank" href="{0}">{1}</a>', permalink_url, response.responseText), drawing_info]]
					Ext.getCmp('save-history-action').store.loadData(data, true);
				},
				failure: function(response, opts) {
					Ext.MessageBox.alert("Error", "Failed to save data.");
				}
			});
		} else {
			Ext.MessageBox.alert("Warning", "There is no data to be saved.");
		}
	},
});
mappanel.getTopToolbar().add(action);
