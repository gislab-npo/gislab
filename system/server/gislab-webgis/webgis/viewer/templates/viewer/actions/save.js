
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
					Ext.get('geojson-link').dom.href = '{% url "webgis.storage.views.ball" %}?ID='+response.responseText;
					Ext.get('geojson-link').update(response.responseText);
					// to make it work like non-toggle button
					save_action.toggle(false);
					//window.location.assign('{% url "webgis.storage.views.ball" %}?ID='+response.responseText);
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
var geojson_link = {
	id: 'geojson-link',
	xtype: 'box',
	autoEl: {tag: 'a', href: '#', html: ''}
}
mappanel.getTopToolbar().add('-', action, geojson_link);

