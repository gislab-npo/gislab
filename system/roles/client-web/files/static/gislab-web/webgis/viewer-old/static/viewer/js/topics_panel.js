WebGIS.TopicsPanel = Ext.extend(Ext.tree.TreePanel, {
	topics: null,

	constructor: function(config) {
		this.map = config.map;
		config.root = this.createTopicsData(config.topics);
		//config.useArrows = true;
		config.rootVisible = false;
		WebGIS.TopicsPanel.superclass.constructor.apply(this, arguments);
	},
	createTopicsData: function(topics) {
		var root = new Ext.tree.TreeNode({
			text: '',
			leaf: false,
			expanded: true
		});
		Ext.each(topics, function(topic) {
			var node = new Ext.tree.TreeNode({
				text: topic.title,
				leaf: true,
				expanded: true,
				checked: false,
				listeners: {
					beforechildrenrendered: function(node) {
						node.getUI().elNode.setAttribute('depth', node.getDepth());
						node.getUI().checkbox.setAttribute('type', 'radio');
						node.getUI().checkbox.setAttribute('name', 'topics-radio');

						var info_button = document.createElement('button');
						info_button.setAttribute('class', 'layer-info');
						node.getUI().getEl().children[0].insertBefore(info_button, node.getUI().getEl().children[0].children[0]);
					},
					checkchange: function(node) {
						var topic = node.attributes.topic;
						
					}.bind(this),
					click: function(node, evt) {
						if (evt.getTarget().tagName === 'INPUT') {
							var checkbox = evt.getTarget();
							checkbox.click();
							Ext.getCmp('layers-tree-panel').root.setVisibleLayers(node.attributes.topic.visible_overlays, true);
							root._selected_topic = checkbox;
						} else if (evt.getTarget().className === "layer-info") {
							var visible_overlays = node.attributes.topic.visible_overlays;
							var indent = '';
							var visit_node = function(node) {
								if (node.hasChildNodes()) {
									indent += '&nbsp;&nbsp;';
									var children_content = [];
									Ext.each(node.childNodes, function(child) {
										var child_content = visit_node(child);
										if (child_content) {
											children_content.push(child_content);
										}
									});
									indent = indent.slice(12);
									if (children_content.length > 0) {
										if (node.getDepth() > 0) {
											return indent+'<label class="layer-group">'+node.attributes.text+'</label><br />'+children_content.join('');
										} else {
											return children_content.join('');
										}
									}
								} else if (visible_overlays.indexOf(node.attributes.text) != -1) {
									return '<span>'+indent+'- '+node.attributes.text+'</span><br />';
								}
							};
							var topic_metadata = String.format('<div class="layer-info-panel">\
									<label class="layer-group">{0}:</label><br />{1}<br /><br />\
									<label class="layer-group">{2}:</label><br />{3}</div>',
									gettext('Abstract'),
									node.attributes.topic.abstract,
									gettext('Layers'),
									visit_node(Ext.getCmp('layers-tree-panel').root));
							if (root._topicInfoWindow) {
								if (root._topicInfoWindow.target.getAttribute('id') === evt.getTarget().parentElement.getAttribute('id')) {
									root._topicInfoWindow.destroy();
									root._topicInfoWindow = null;
									return;
								} else {
									root._topicInfoWindow.destroy();
								}
							}
							var t = new Ext.ToolTip({
								anchor: 'right',
								anchorToTarget: true,
								target: evt.getTarget().parentElement,
								title: node.attributes.topic.title,
								html: topic_metadata,
								closable: true,
								autoHide: false,
								autoScroll: true,
								width: 300,
								maxHeight: 100,
								listeners: {
									hide: function(t) {
										t.destroy();
									}
								}
							});
							t.show();
							root._topicInfoWindow = t;
						}
					},
					beforedblclick: function(node, evt) {
						node.getUI().toggleCheck(true);
						return false;
					}
				}
			});
			node.attributes.topic = topic;
			root.appendChild(node);
		});
		return root;
	},
	listeners: {
		deactivate: function(panel) {
			if (panel.root._topicInfoWindow) {
				panel.root._topicInfoWindow.destroy();
			}
		},
		afterrender: function(panel) {
			var overlays_root = Ext.getCmp('layers-tree-panel').root;
			overlays_root.on('layerchange', function(root, layer, visible_layers) {
				if (panel.root._selected_topic) {
					panel.root._selected_topic.checked = false;
					panel.root._selected_topic = null;
				}
			});
		}
	}
});
