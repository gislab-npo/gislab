
// save ball
var action = new Ext.Action({
	id: 'save-action',
	cls: 'x-btn-icon',
	iconCls: 'save-icon',
	tooltip: 'Save drawing',
	toggleGroup: 'tools', // to disable drawing tools that could cause to export control points of OpenLayers.Control.ModifyFeature tool
	handler: function(save_action) {
		var features_layers = [points_layer, lines_layer, polygons_layer];
		var features = [];
		Ext.each(features_layers, function(layer) {
			features = features.concat(layer.features);
		});
		if (features.length > 0) {
			var geojson = new OpenLayers.Format.GeoJSON().write(features, true);
			// add projection info
			if (mappanel.map.projection) {
				var geojson_obj = JSON.parse(geojson);
				geojson_obj.crs = new OpenLayers.Format.GeoJSON().createCRSObject(features[0]);
				geojson = JSON.stringify(geojson_obj, null, '    ');
			}
			Ext.Ajax.request({
				method: 'POST',
				url: '{% url "webgis.storage.views.ball" %}',
				jsonData: geojson,
				headers: { 'Content-Type': 'application/geojson; charset=utf-8' },
				success: function(response) {
					vector_data_balls = response.responseText;
					Ext.state.Manager.set("map", {balls: [response.responseText]});
					Ext.getCmp('geojson-links').setLinks([{
						text: response.responseText,
						href: Ext.urlAppend('{% url "webgis.storage.views.ball" %}', Ext.urlEncode({ID: response.responseText})),
					}]);

					// Add record into saving history
					var permalink_url = Ext.get('permalink').dom.children[0].href;
					var drawing_info = String.format('points: {0} lines: {1} polygons: {2}', points_layer.features.length, lines_layer.features.length, polygons_layer.features.length);
					var data = [[new Date(), String.format('<a href="{0}">{1}</a>', permalink_url, response.responseText), drawing_info]]
					Ext.getCmp('save-history-action').store.loadData(data, true);

					// to make it work like non-toggle button
					save_action.toggle(false);
				},
				failure: function(response, opts) {
					Ext.MessageBox.alert("Error", "Failed to save data.");
				}
			});
		} else {
			Ext.MessageBox.alert("Warning", "There is no data to be saved.");
		}
	}
});
mappanel.getTopToolbar().add('-', action);
