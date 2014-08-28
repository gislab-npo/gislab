WebGIS.TopicsAction = Ext.extend(Ext.Action, {
	window: null,

	constructor: function(config) {
		this.topics = config.topics;
		WebGIS.TopicsAction.superclass.constructor.apply(this, arguments);
	},

	showTopics: function() {
		if (!this.window) {
			this.window = new Ext.Window({
				id: 'topics-window',
				header: false,
				closable: false,
				resizable: false,
				width: 260,
				height: 450,
				layout: 'border',
				baseAction: this,
				items: [
					{
						xtype: 'panel',
						region: 'east',
						ref: 'topicDetailsPanel',
						cls: 'topic-detail-panel',
						width: 330,
						header: false,
						collapsible: true,
						collapsed: true,
						animCollapse: false,
						collapseMode: 'mini',
						floatable: false,
						layout: {
							type: 'vbox',
							align: 'stretch'
						},
						items: [
							{
								xtype: 'label',
								text: gettext('Abstract')+':',
							}, {
								xtype: 'textarea',
								ref: '/abstractField',
								readOnly: true,
								height: 70,
								text: ''
							}, {
								xtype: 'label',
								text: gettext('Layers')+':',
							}, {
								xtype: 'box',
								id: 'topic-visible-layers',
								cls: 'topic-layers',
								ref: '/visibleLayersField',
								html: '',
								flex: 1
							}
						],
						listeners: {
							beforecollapse: function(panel) {
								var window = panel.ownerCt;
								window.setSize(260, window.height);
							},
							beforeexpand: function(panel) {
								var window = panel.ownerCt;
								window.setSize(590, window.height);
							}
						},
					}, {
						xtype: 'panel',
						layout: 'fit',
						title: gettext('Topics'),
						region: 'center',
						cls: 'topics-panel',
						tools: [{
							id: 'right',
							handler: function(event, toolEl, panel, tc) {
								var detailsPanel = panel.ownerCt.topicDetailsPanel;
								detailsPanel.toggleCollapse();
								if (!detailsPanel.collapsed) {
									panel.addClass('details-expanded');
								} else {
									panel.removeClass('details-expanded');
								}
							}
						}],
						bbar: ['->',
							{
								xtype: 'tbbutton',
								text: gettext('Load'),
								width: 80,
								handler: function(button) {
									var window = button.ownerCt.ownerCt.ownerCt;
									var selected_records = window.topicsList.getSelectedRecords();
									if (selected_records.length == 1) {
										Ext.getCmp('layers-tree-panel').root.setVisibleLayers(selected_records[0].get("visible_overlays"));
										window.hide();
									}
								}
							}
						],
						items: {
							xtype: 'listview',
							ref: '/topicsList',
							hideHeaders: true,
							columns: [{
								dataIndex: 'title',
							}],
							columnSort: false,
							store: new Ext.data.JsonStore({
								fields: [
									{name: 'title', type: 'string'},
									{name: 'abstract', type: 'string'},
									{name: 'visible_overlays'}
								],
								data: this.topics,
							}),
							singleSelect: true,
							stateful: true,
							listeners: {
								click: function(listview, index, node, e ) {
									var record = listview.store.getAt(index);
									var visible_overlays = record.get("visible_overlays");
									listview.ownerCt.ownerCt.abstractField.setValue(record.get("abstract"));
									var text = '';
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
									text = visit_node(Ext.getCmp('layers-tree-panel').root);
									listview.ownerCt.ownerCt.visibleLayersField.update(text);
								},
								dblclick: function(listview, index, node, e ) {
									var record = listview.store.getAt(index);
									var window = listview.ownerCt.ownerCt;
									Ext.getCmp('layers-tree-panel').root.setVisibleLayers(record.get("visible_overlays"));
									window.hide();
								}
							}
						}
					}
				],
				listeners: {
					hide: function(window) {
						Ext.getCmp(window.baseAction.itemId).toggle(false);
					}
				}
			});
		}
		this.window.show();
		this.window.alignTo(Ext.getCmp('map-panel').getTopToolbar().getId(), 'tl-bl', [5, 0]);
	}
});
