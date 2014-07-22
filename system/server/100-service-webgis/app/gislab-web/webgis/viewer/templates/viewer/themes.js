{% load i18n %}

var action = new WebGIS.ThemesAction({
	id: 'themes-action',
	themes: JSON.parse('{{ themes|default:"[]"|escapejs }}'),
	cls: 'x-btn-icon',
	iconCls: 'themes-icon',
	enableToggle: true,
	toggleGroup: 'themes',
	tooltip: '{% trans "Map themes" %}',
	toggleHandler: function(action, toggled) {
		if (toggled) {
			action.baseAction.showThemes();
		} else {
			if (action.baseAction.window) {
				action.baseAction.window.close();
			}
		}
	},
})
mappanel.getTopToolbar().add(action);
