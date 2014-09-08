{% load i18n %}
//Zoom to max extent action
action = new GeoExt.Action({
	handler: function() { mappanel.map.setCenter(map.getMaxExtent().getCenterLonLat(), 0); },
	map: mappanel.map,
	cls: 'x-btn-icon',
	iconCls: 'zoom-to-max-icon',
	tooltip: '{% trans "Zoom to max extent" %}'
});
mappanel.getTopToolbar().add(' ', action);

// Navigation history - two 'button' controls
ctrl = new OpenLayers.Control.NavigationHistory();
mappanel.map.addControl(ctrl);

action = new GeoExt.Action({
	control: ctrl.previous,
	disabled: true,
	cls: 'x-btn-icon',
	iconCls: 'previous-icon',
	tooltip: '{% trans "Previous in history" %}',
});
mappanel.getTopToolbar().add(' ', action);

action = new GeoExt.Action({
	control: ctrl.next,
	disabled: true,
	cls: 'x-btn-icon',
	iconCls: 'next-icon',
	tooltip: '{% trans "Next in history" %}',
});
mappanel.getTopToolbar().add(' ', action);
