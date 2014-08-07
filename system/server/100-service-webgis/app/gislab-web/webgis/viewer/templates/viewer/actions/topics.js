{% load i18n %}

var topics = JSON.parse('{{ topics|default:"[]"|escapejs }}');
if (topics.length === 0) {
	topics.push({
		'title': '{% trans "Default topic" %}',
		'abstract': '{% trans "Default layers configuration" %}',
		'visible_overlays': overlays_root.getVisibleLayers()
	});
}
var action = new WebGIS.TopicsAction({
	id: 'topics-action',
	topics: topics,
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
				action.baseAction.window.hide();
			}
		}
	},
})
mappanel.getTopToolbar().add(action);
