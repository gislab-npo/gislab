{% load i18n %}

var action = new WebGIS.TopicsAction({
	id: 'topics-action',
	topics: JSON.parse('{{ topics|default:"[]"|escapejs }}'),
	cls: 'x-btn-icon',
	iconCls: 'topics-icon',
	enableToggle: true,
	toggleGroup: 'topics',
	tooltip: '{% trans "Map topics" %}',
	toggleHandler: function(action, toggled) {
		if (toggled) {
			action.baseAction.showTopics();
		} else {
			if (action.baseAction.window) {
				action.baseAction.window.close();
			}
		}
	},
})
mappanel.getTopToolbar().add(action);
