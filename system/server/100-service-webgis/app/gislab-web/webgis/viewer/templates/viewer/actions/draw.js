{% load i18n %}
var draw_controls = [
	// Draw points control
	{
		title: '{% trans "Points" %}',
		iconCls: 'draw-point-icon',
		control: new OpenLayers.Control.DrawFeature(
			points_layer,
			OpenLayers.Handler.Point,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						title: '-',
						description: '-'
					};
					// update feature on map
					feature.layer.drawFeature(feature);
					feature.layer.events.triggerEvent("featuremodified", {feature: feature});
				}
			}
		)
	},

	// Draw lines control
	{
		title: '{% trans "Lines" %}',
		iconCls: 'draw-line-icon',
		control: new OpenLayers.Control.DrawFeature(
			lines_layer,
			OpenLayers.Handler.Path,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						title: '-',
						description: '-'
					};
					// update feature on map
					feature.layer.drawFeature(feature);
					feature.layer.events.triggerEvent("featuremodified", {feature: feature});
				}
			}
		)
	},

	// Draw polygons control
	{
		title: '{% trans "Polygons" %}',
		iconCls: 'draw-polygon-icon',
		control: new OpenLayers.Control.DrawFeature(
			polygons_layer,
			OpenLayers.Handler.Polygon,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						title: '-',
						description: '-'
					};
					// update feature on map
					feature.layer.drawFeature(feature);
					feature.layer.events.triggerEvent("featuremodified", {feature: feature});
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
	iconCls: 'draw-icon',
	enableToggle: true,
	toggleGroup: 'measure-draw',
	tooltip: '{% trans "Draw on map" %}',
	{% if user.is_guest %}
	drawingsHistoryProxy: new WebGIS.DrawingsLocalStorageProxy({
		data: {count: 0, drawings: []},
		storagePrefix: 'gislab-{{ project }}'
	}),
	{% else %}
	drawingsHistoryProxy: new WebGIS.DrawingsHttpProxy({
		url: Ext.urlAppend('{% url "storage:drawing" %}', Ext.urlEncode({user: '{{ user.username }}', project: '{{ project }}'})),
		user: '{{ user.username }}',
		project: '{{ project }}'
	}),
	{% endif %}
	drawingUrl: '{% url "storage:ball" %}',
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
					var data = {
						time: new Date(),
						title: title,
						permalink: Ext.get('permalink').dom.children[0].href.split('?')[1],
						drawing: response.responseText,
						statistics: String.format('{0} POINTS, {1} LINESTRINGS, {2} POLYGONS', points_layer.features.length, lines_layer.features.length, polygons_layer.features.length)
					};
					this.historyStore.proxy.saveRecord(data);
				}.bind(drawAction),
				failure: function(response, opts) {
					Ext.MessageBox.show({
						title: '{% trans "Error" %}',
						msg: '{% trans "Failed to save data" %}',
						minWidth: 300,
						closable: false,
						modal: true,
						buttons: Ext.Msg.OK,
					});
				}
			});
		} else {
			Ext.MessageBox.show({
				title: '{% trans "Error" %}',
				msg: '{% trans "There is no data to be saved" %}',
				minWidth: 300,
				closable: false,
				modal: true,
				buttons: Ext.Msg.OK,
			});
		}
	},
	importFeatures: function(features, makeCopy, skipDuplicit) {
		var points = [];
		var lines = [];
		var polygons = [];
		Ext.each(features, function(f) {
			if (skipDuplicit) {
				if (points_layer.getFeaturesByAttribute('title', f.attributes.title).length ||
					lines_layer.getFeaturesByAttribute('title', f.attributes.title).length ||
					polygons_layer.getFeaturesByAttribute('title', f.attributes.title).length) {
					return true; //continue
				}
			}
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
				if (f.geometry.CLASS_NAME === 'OpenLayers.Geometry.Point')
					points.push(f);
				if (f.geometry.CLASS_NAME === 'OpenLayers.Geometry.LineString')
					lines.push(f);
				if (f.geometry.CLASS_NAME === 'OpenLayers.Geometry.Polygon')
					polygons.push(f);
			});
		});
		points_layer.addFeatures(points);
		lines_layer.addFeatures(lines);
		polygons_layer.addFeatures(polygons);
	},
});
mappanel.getTopToolbar().add(action);
