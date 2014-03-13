
//Home Action
action = new GeoExt.Action({
	handler: function() { mappanel.map.zoomToExtent(zoom_extent, true); },
	map: mappanel.map,
	cls: 'x-btn-icon',
	iconCls: 'home-icon',
	tooltip: 'Home'
});
mappanel.getTopToolbar().add(action);

//Pan Map Action
action = new GeoExt.Action({
	control: new OpenLayers.Control.MousePosition({formatOutput: function(lonLat) {return '';}}),
	map: mappanel.map,
	toggleGroup: 'tools',
	group: 'tools',
	cls: 'x-btn-icon',
	iconCls: 'pan-icon',
	tooltip: 'Pan'
});
mappanel.getTopToolbar().add(action);

// Navigation history - two 'button' controls
ctrl = new OpenLayers.Control.NavigationHistory();
mappanel.map.addControl(ctrl);

action = new GeoExt.Action({
	control: ctrl.previous,
	disabled: true,
	cls: 'x-btn-icon',
	iconCls: 'previous-icon',
	tooltip: 'Previous in history',
});
mappanel.getTopToolbar().add(action);

action = new GeoExt.Action({
	control: ctrl.next,
	disabled: true,
	cls: 'x-btn-icon',
	iconCls: 'next-icon',
	tooltip: 'Next in history',
});
mappanel.getTopToolbar().add(action);
