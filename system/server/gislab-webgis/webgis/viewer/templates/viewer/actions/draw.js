
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
						title: ''
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
						title: ''
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
						title: ''
					};
					// update feature on map
					polygons_layer.drawFeature(feature);
				}
			}
		)
	}
];

action = new WebGIS.DrawAction({
	id: 'draw-action',
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
				url: '{% url "storage:ball" %}',
				jsonData: geojson,
				headers: { 'Content-Type': 'application/geojson; charset=utf-8' },
				success: function(response) {
					drawings_param = response.responseText;
					Ext.state.Manager.set("map", {drawings: [response.responseText]});
					Ext.getCmp('geojson-links').setLinks([{
						name: title,
						hyperlink_text: response.responseText,
						href: Ext.urlAppend('{% url "storage:ball" %}', Ext.urlEncode({ID: response.responseText})),
					}]);

					// Add record into saving history
					var permalink_url = Ext.get('permalink').dom.children[0].href;
					var drawing_info = String.format('Points: {0}<br />Lines: {1}<br />Polygons: {2}', points_layer.features.length, lines_layer.features.length, polygons_layer.features.length);
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
	importFeatures: function(features, makeCopy) {
		var points = [];
		var lines = [];
		var polygons = [];
		Ext.each(features, function(f) {
			var converted_features = [];
			// break feature with multipoint, multilinestrings or multipolygons geom type to multiple features
			// with simple geometry type and copy/create only supported attributes
			if (f.geometry.components || makeCopy) {
				var geometries = f.geometry.CLASS_NAME.indexOf('Multi') != -1? f.geometry.components : [f.geometry];
				Ext.each(geometries, function(geom) {
					var attributes = {
						title: f.attributes.title? f.attributes.title : '',
						description: f.attributes.description? f.attributes.description : '',
					};
					converted_features.push(new OpenLayers.Feature.Vector(geom, attributes));
				});
			} else {
				converted_features = [f];
			}
			Ext.each(converted_features, function(f) {
				if (f.geometry.CLASS_NAME == 'OpenLayers.Geometry.Point')
					points.push(f);
				if (f.geometry.CLASS_NAME == 'OpenLayers.Geometry.LineString')
					lines.push(f);
				if (f.geometry.CLASS_NAME == 'OpenLayers.Geometry.Polygon')
					polygons.push(f);
			});
		});
		points_layer.addFeatures(points);
		lines_layer.addFeatures(lines);
		polygons_layer.addFeatures(polygons);
	},
});
mappanel.getTopToolbar().add(action);
