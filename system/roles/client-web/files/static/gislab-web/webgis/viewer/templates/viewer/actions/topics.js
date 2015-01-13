{% load i18n %}

var topics = JSON.parse('{{ topics|default:"[]"|escapejs }}');
var action = new WebGIS.TopicsAction({
	id: 'topics-action',
	topics: topics,
	cls: 'x-btn-icon',
	iconCls: 'topics-icon',
	enableToggle: true,
	toggleGroup: 'topics',
	tooltip: '{% trans "Topics" %}',
	toggleHandler: function(action, toggled) {
		if (toggled) {
			action.baseAction.showTopics();
		} else {
			if (action.baseAction.window) {
				action.baseAction.window.hide();
			}
		}
	},
})
mappanel.getTopToolbar().add(action);
