//Search Action

var layers_data = {
	layers: [
{% for layer in layers %}
		{
			name: '{{ layer.name }}',
			value: '{{ layer.name }}',
			attributes: [
			{% for attrib in layer.attributes %}
				{name: '{{ attrib.name }}', type: '{{ attrib.type }}'},
			{% endfor %}
			]
		},
{% endfor %}
	]
};

var searchWindow = new Ext.Window({
	id: 'search-toolbar-window',
	flex: 1,
	layout: {
		type: 'vbox',
		pack: 'start'
	},
	resizable: false,
	closable: false,
	scrollable: false,
	listeners: {
		afterLayout: function(window, layout) {
			window.setHeight(window.getTopToolbar().getHeight()+16+28*window.items.length);
			window.logicalOperator.setDisabled(window.items.length < 2);
		},
		beforeshow: function(window) {
			// calculate window's width from toolbar size
			var toolbar = window.getTopToolbar();
			var first_toolbar_item = toolbar.items.first();
			var last_toolbar_item = toolbar.items.last();
			var toolbar_width = last_toolbar_item.getPosition()[0]-first_toolbar_item.getPosition()[0]+last_toolbar_item.getWidth();
			window.setWidth(toolbar_width+2*(first_toolbar_item.getPosition()[0]-window.getPosition()[0]));
			if (window.items.length == 0) {
				window.addAttribute();
			}
		}
	},
	onLayerChanged: function(layer_record) {
		this.items.each(function(attrib_item) {
			attributes_combo = attrib_item.attributeName;
			attributes_combo.store.loadData(layer_record.json);
			if (attributes_combo.getStore().getCount() > 0) {
				var record = attributes_combo.getStore().getAt(0);
				attributes_combo.setValue(record.get('name'));
				attributes_combo.fireEvent('select', attributes_combo, record, 0);
			}
		});
	},
	updateControlButtons: function() {
		var last_item_index = this.items.length -1;
		this.items.each(function(attrib_item, index) {
			if (index == last_item_index) {
				attrib_item.removeButton.setVisible(index > 0);
				attrib_item.addButton.show();
			} else {
				attrib_item.removeButton.show();
				attrib_item.addButton.hide();
			}
		});
	},
	addAttribute: function() {
		var layer_combo = this.activeLayer;
		var layer_item_index = layer_combo.getStore().find('name', layer_combo.getValue());
		var attributes_data;
		if (layer_item_index != -1) {
			attributes_data = layer_combo.getStore().getAt(layer_item_index).json;
		} else {
			attributes_data = {attributes: []};
		}
		this.add({
			xtype: 'container',
			width: this.getTopToolbar().getWidth(),
			height: 28,
			style: {
				padding: '3px 1px 3px 1px'
			},
			layout : {
				type: 'hbox',
				align : 'stretch'
			},
			items: [
				{
					xtype: 'combo',
					ref: 'attributeName',
					width: 153,
					mode: 'local',
					triggerAction: 'all',
					forceSelection: false,
					store: new Ext.data.JsonStore({
						data: attributes_data,
						storeId: 'search-attributes-store',
						root: 'attributes',
						fields: [{
							name: 'name',
							type: 'string'
						}, {
							name: 'type',
							type: 'string'
						}]
					}),
					valueField: 'name',
					displayField: 'name',
					listeners: {
						select: function (combo, record, index) {
							var operators_combo = combo.ownerCt.attributeOperator;
							var attrib_type = record.json['type'];
							if (combo.attrib_type == attrib_type) {
								return;
							}
							combo.attrib_type = attrib_type;
							combo.ownerCt.valueField.setType(attrib_type);
							if (attrib_type == 'integer' || attrib_type == 'double') {
								operators = [
									{name: '=', value: '='},
									{name: '!=', value: '!='},
									{name: '<', value: '<'},
									{name: '<=', value: '<='},
									{name: '>', value: '>'},
									{name: '>=', value: '>='},
									{name: 'IN', value: 'IN'},
								]
							} else {
								operators = [
									{name: '=', value: '='},
									{name: '!=', value: '!='},
									{name: 'LIKE', value: 'LIKE'},
									{name: 'IN', value: 'IN'},
								]
							}
							operators_combo.store.loadData({operators: operators});
							if (operators_combo.getStore().getCount()) {
								var record = operators_combo.getStore().getAt(0);
								operators_combo.setValue(record.get('name'));
								operators_combo.fireEvent('select', operators_combo, record, 0);
							}
						}
					}
				}, {
					xtype: 'combo',
					ref: 'attributeOperator',
					width: 55,
					mode: 'local',
					triggerAction: 'all',
					forceSelection: true,
					store: new Ext.data.JsonStore({
						data: {operators: []},
						storeId: 'search-operator-store',
						root: 'operators',
						fields: [{
							name: 'name',
							type: 'string'
						}]
					}),
					valueField: 'name',
					displayField: 'name',
					listeners: {
						select: function (combo, record, index) {
							combo.ownerCt.valueField.setMultiMode(record.get('name') == 'IN');
						}
					}
				}, {
					xtype: 'container',
					ref: 'valueField',
					layout: 'fit',
					flex: 1,
					items: [{
						xtype: 'textfield',
						disabled: true
					}],

					setType: function(type) {
						this.multiMode = false;
						this.type = type;
						this.multiMode = false;
						this.createValueField();
					},
					setMultiMode: function(multi) {
						if (multi != this.multiMode && this.type != 'text') {
							this.multiMode = multi;
							this.createValueField();
						} else {
							this.multiMode = multi;
						}
					},
					createValueField: function() {
						this.removeAll();
						var comp;
						if (this.type == 'integer') {
							if (this.multiMode) {
								comp = {
									xtype: 'textfield',
									regex: /^\d+(\s*,\s*\d+)*$/,
									regexText:'Incorrect comma-separated list of integers',
								}
							} else {
								comp = {
									xtype: 'numberfield',
									allowDecimals: false,
								}
							}
						} else if (this.type == 'double') {
							if (this.multiMode) {
								comp = {
									xtype: 'textfield',
									regex: /^\d+(\.\d+)?(\s*,\s*\d+(\.\d+)?)*$/,
									regexText:'Incorrect comma-separated list of numbers',
								}
							} else {
								comp = {
									xtype: 'numberfield',
									allowDecimals: true,
									decimalSeparator: '.'
								}
							}
						} else {
							comp = {
								xtype: 'textfield',
								allowDecimals: false
							}
						}
						this.add(comp);
						this.doLayout();
					},
					getValue: function() {
						return this.get(0).getValue();
					}
				}, {
					xtype: 'container',
					itemId: 'control-buttons',
					layout: 'hbox',
					width: 38,
					cls: 'search-control-buttons',
					items: [
						{
							xtype: 'button',
							itemId: 'add-button',
							cls: 'x-btn-icon',
							iconCls: 'add-icon',
							tooltip: 'Add another attribute filter',
							ref: './addButton',
							handler: function(button) {
								var search_window = button.ownerCt.ownerCt.ownerCt;
								search_window.addAttribute();
							}
						}, {
							xtype: 'box',
							flex: 1
						}, {
							xtype: 'button',
							itemId: 'remove-button',
							cls: 'x-btn-icon',
							iconCls: 'remove-icon',
							tooltip: 'Remove attribute filter',
							ref: './removeButton',
							handler: function(button) {
								var window = button.ownerCt.ownerCt.ownerCt;
								// remove whole attribute container
								window.remove(button.ownerCt.ownerCt);
								search_window.updateControlButtons();
								window.doLayout();
							}
						}
					]
				}
			]
		});
		this.doLayout();
		this.updateControlButtons();
	},
	tbar: [
		{
			xtype: 'tbspacer'
		}, {
			xtype: 'combo',
			ref: '/activeLayer',
			width: 150,
			mode: 'local',
			triggerAction: 'all',
			forceSelection: true,
			store: new Ext.data.JsonStore({
				data: layers_data,
				storeId: 'search-layer-store',
				root: 'layers',
				fields: [{
					name: 'name',
					type: 'string'
				}, {
					name: 'value',
					type: 'string'
				}]
			}),
			valueField: 'value',
			displayField: 'name',
			listeners: {
				afterrender: function(combo) {
					if (combo.getStore().getCount() > 0) {
						var recordSelected = combo.getStore().getAt(0);
						combo.setValue(recordSelected.get('name'));
						combo.fireEvent('select', combo, recordSelected, 0);
					}
				},
				select: function (combo, record, index) {
					search_window = Ext.getCmp('search-toolbar-window');
					search_window.onLayerChanged(record);
				}
			}
		}, {
			xtype: 'tbspacer'
		}, {
			xtype: 'label',
			text: 'Logical operator:'
		}, {
			xtype: 'tbspacer'
		}, {
			xtype: 'combo',
			ref: '/logicalOperator',
			width: 50,
			mode: 'local',
			tooltip: 'Logical operator between attributes',
			triggerAction: 'all',
			forceSelection: true,
			store: new Ext.data.ArrayStore({
				data: [['AND'], ['OR']],
				storeId: 'search-logical-operators-store',
				fields: [{
					name: 'value',
					type: 'string'
				}]
			}),
			valueField: 'value',
			displayField: 'value',
			listeners: {
				afterrender: function(combo) {
					Ext.QuickTips.register({ target: combo.getEl(), text: combo.tooltip });
					var recordSelected = combo.getStore().getAt(0);
					combo.setValue(recordSelected.get('value'));
				},
			}
		}, {
			xtype: 'tbspacer'
		}, {
			xtype: 'label',
			text: 'Limit:'
		}, {
			xtype: 'tbspacer'
		}, {
			xtype: 'spinnerfield',
			ref: '/limit',
			width: 50,
			mode: 'local',
			triggerAction: 'all',
			allowNegative: false,
			minValue: 1,
			maxValue: 1000,
			value: 50
		}, {
			xtype: 'tbspacer'
		}, new Ext.Action({
			text: 'Search',
			tooltip: 'Search',
			cls: 'x-btn-text',
			format: new OpenLayers.Format.GML(),

			handler: function(action) {
				var search_window = Ext.getCmp('search-toolbar-window');
				var layer = search_window.activeLayer.getValue();
				var logical_operator = search_window.logicalOperator.getValue();
				var features_count = search_window.limit.getValue();
				var attributes_queries = [];
				search_window.items.each(function(attrib_item) {
					var attribute = attrib_item.attributeName.getValue();
					if (attribute) {
						var operator = attrib_item.attributeOperator.getValue();
						var value = attrib_item.valueField.getValue().toString();
						if (operator == 'IN') {
							// Format to proper list value string. Spaces are very important. Example: " ( 'val1' , 'val2' , ... ) "
							var list_values = [];
							Ext.each(value.split(','), function(list_value) {
								list_values.push(list_value.trim());
							});
							value = String.format(" ( '{0}' ) ", list_values.join("' , '"));
						} else {
							value = String.format("'{0}'", value);
						}
						attributes_queries.push(String.format('"{0}" {1} {2}', attribute, operator, value))
					}
				});

				var query_filter = String.format('{0}:{1}', layer, attributes_queries.join(String.format(' {0} ', logical_operator)));
				Ext.Ajax.request({
					method: 'GET',
					url: '{{ getfeatureinfo_url }}',
					params: {
						SERVICE: 'WMS',
						REQUEST: 'GetFeatureInfo',
						FEATURE_COUNT: features_count,
						INFO_FORMAT: 'application/vnd.ogc.gml',
						SRS: '{{ projection }}',
						LAYERS: layer,
						QUERY_LAYERS: layer,
						FILTER: query_filter
					},
					scope: this,
					success: function(response) {
						var doc = response.responseXML;
						if(!doc || !doc.documentElement) {
							doc = response.responseText;
						}
						var features = this.format.read(doc);
						Ext.getCmp('featureinfo-panel').showFeatures(features);
					},
					failure: function(response, opts) {
						Ext.MessageBox.alert("Error", "Searching failed.");
					}
				});
			}
		}),
	],
	items: []
});

action = new Ext.Action({
	xtype: 'action',
	cls: 'x-btn-icon',
	iconCls: 'search-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	tooltip: 'Search',
	toggleHandler: function(button, toggled) {
		if (toggled) {
			searchWindow.show();
			searchWindow.alignTo(mappanel.getTopToolbar().getId(), 'bl', [70, 4]);
		} else {
			searchWindow.hide();
			//Ext.getCmp('featureinfo-panel').clearFeaturesLayers();
			Ext.getCmp('featureinfo-panel').collapse();
		}
	},
});
mappanel.getTopToolbar().add('-', action);
