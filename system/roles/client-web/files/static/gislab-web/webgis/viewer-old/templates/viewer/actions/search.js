{% load i18n %}
//Search Action

action = new WebGIS.SearchAction({
	xtype: 'action',
	map: mappanel.map,
	url: '{{ ows_url }}',
	cls: 'x-btn-icon',
	iconCls: 'search-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	tooltip: '{% trans "Search features by attributes" %}',
	toggleHandler: function(action, toggled) {
		if (toggled) {
			action.baseAction.showSearchToolbar();
		} else {
			action.baseAction.window.hide();
		}
	},
});
mappanel.getTopToolbar().add(action);
