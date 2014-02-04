
// Draw points action
ctrl = new OpenLayers.Control.DrawFeature(
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
);
action = new WebGIS.DrawAction({
	control: ctrl,
	map: mappanel.map,
	snappingLayerTargets: [points_layer, lines_layer, polygons_layer],
	dialogTitle: 'Points',
	cls: 'x-btn-icon',
	iconCls: 'draw-point-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	tooltip: 'Draw points',
	toggleHandler: function(action, toggled) {
		action.baseAction.toggleHandler(action, toggled);
	}
});
mappanel.getTopToolbar().add('-', action);

// Draw lines action
ctrl = new OpenLayers.Control.DrawFeature(
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
);
action = new WebGIS.DrawAction({
	control: ctrl,
	map: mappanel.map,
	snappingLayerTargets: [points_layer, lines_layer, polygons_layer],
	dialogTitle: 'Lines',
	cls: 'x-btn-icon',
	iconCls: 'draw-line-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	tooltip: 'Draw lines',
	toggleHandler: function(action, toggled) {
		action.baseAction.toggleHandler(action, toggled);
	}
});
mappanel.getTopToolbar().add(action);

// Draw polygons action
ctrl = new OpenLayers.Control.DrawFeature(
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
);
action = new WebGIS.DrawAction({
	control: ctrl,
	map: mappanel.map,
	snappingLayerTargets: [points_layer, lines_layer, polygons_layer],
	dialogTitle: 'Polygons',
	cls: 'x-btn-icon',
	iconCls: 'draw-polygon-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	tooltip: 'Draw polygons',
	toggleHandler: function(action, toggled) {
		action.baseAction.toggleHandler(action, toggled);
	}
});
mappanel.getTopToolbar().add(action);
