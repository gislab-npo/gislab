//Print Action
var printWindow = new Ext.Window({
	id: 'print-toolbar-window',
	autoHeight: true,
	layout: 'fit',
	resizable: false,
	closable: false,
	listeners: {
		hide: function(window) {
			mappanel.map.events.unregister("zoomend", this, this.updatePrintScales);
			printExtent.hide();
		},
		show: function(window) {
			this.updatePrintScales();
			//printExtent.page.setRotation(0, true);
			mappanel.map.events.register("zoomend", this, this.updatePrintScales);
			printExtent.page.on('change', function(window, mods) {
				if (mods.hasOwnProperty('rotation')) {
					var spinner = Ext.getCmp('print-rotation-spinner');
					if (spinner) {
						spinner.setValue(mods.rotation);
					}
				}
			});
			//window.setWidth(toolbar.getWidth());
			printExtent.show();
		},
		beforeshow: function(window) {
			// calculate window's width from toolbar size
			var toolbar = window.getTopToolbar();
			var first_toolbar_item = toolbar.items.first();
			var last_toolbar_item = toolbar.items.last();
			var toolbar_width = last_toolbar_item.getPosition()[0]-first_toolbar_item.getPosition()[0]+last_toolbar_item.getWidth();
			window.setWidth(toolbar_width+2*(first_toolbar_item.getPosition()[0]-window.getPosition()[0]));
		}
	},
	updatePrintScales: function() {
		var map_scale = Math.round(mappanel.map.getScale());
		{% if scales %}
		// find exact scale value
		var exact_scale;
		var closest_dist = null;
		Ext.each([{{ scales|join:"," }}], function(scale) {
			var dist = Math.abs(map_scale-scale);
			if (closest_dist == null || dist < closest_dist) {
				exact_scale = scale;
				closest_dist = dist;
			}
		});
		map_scale = exact_scale;
		{% endif %}
		printExtent.printProvider.capabilities.scales = [{"name":"1:"+Number(map_scale).toLocaleString(), "value": map_scale}]
		printExtent.printProvider.scales.loadData(printExtent.printProvider.capabilities);
		if (printExtent.pages.length == 0) {
			printExtent.addPage();
		}
		printExtent.page.setScale(printExtent.printProvider.scales.getAt(0), 'm');
	},
	tbar: [{
		xtype: 'combo',
		id: 'print-layouts-combobox',
		width: 100,
		mode: 'local',
		triggerAction: 'all',
		readonly: true,
		store: new Ext.data.JsonStore({
			// store configs
			data: printExtent.printProvider.capabilities,
			storeId: 'print-layouts-store',
			// reader configs
			root: 'layouts',
			fields: [{
				name: 'name',
				type: 'string'
			}, ]
		}),
		valueField: 'name',
		displayField: 'name',
		listeners: {
			afterrender: function(combo) {
				var recordSelected = combo.getStore().getAt(0);
				combo.setValue(recordSelected.get('name'));
				combo.fireEvent('select', combo, recordSelected, 0);
			},
			select: function (combo, record, index) {
				var layout = printExtent.printProvider.layouts.getAt(index); // record value doesn't work
				printExtent.printProvider.setLayout(layout, true);
				var labeld_grid = Ext.getCmp('print-composer-labels-grid');
				var labels_source = {};
				if (layout.json.labels.length > 0) {
					Ext.each(layout.json.labels, function(label) {
						labels_source[label] = '';
					});
					labeld_grid.show();
				} else {
					labeld_grid.hide();
				}
				labeld_grid.setSource(labels_source);
				printWindow.syncShadow();
			}
		}
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'combo',
		id: 'print-dpi-combobox',
		width: 70,
		mode: 'local',
		triggerAction: 'all',
		forceSelection: true,
		store: new Ext.data.JsonStore({
			// store configs
			data: printExtent.printProvider.capabilities,
			storeId: 'print-dpi-store',
			// reader configs
			root: 'dpis',
			fields: [{
				name: 'name',
				type: 'string'
			}, {
				name: 'value',
				type: 'int'
			}]
		}),
		valueField: 'value',
		displayField: 'name',
		listeners: {
			afterrender: function(combo) {
				var recordSelected = combo.getStore().getAt(0);
				combo.setValue(recordSelected.get('name'));
				combo.fireEvent('select', combo, recordSelected, 0);
			},
			select: function (combo, record, index) {
				printExtent.printProvider.setDpi(record);
			}
		}
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'combo',
		id: 'print-format-combobox',
		width: 70,
		mode: 'local',
		triggerAction: 'all',
		forceSelection: true,
		store: new Ext.data.JsonStore({
			// store configs
			data: printExtent.printProvider.capabilities,
			storeId: 'print-format-store',
			// reader configs
			root: 'outputFormats',
			fields: [{
				name: 'name',
				type: 'string'
			}]
		}),
		valueField: 'name',
		displayField: 'name',
		listeners: {
			afterrender: function(combo) {
				var recordSelected = combo.getStore().getAt(0);
				combo.setValue(combo.getStore().getAt(0).get('name'));
			}
		}
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'label',
		text: 'Rotation'
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'spinnerfield',
		id: 'print-rotation-spinner',
		width: 60,
		value: 0,
		allowNegative: true,
		autoStripChars: true,
		allowDecimals: false,
		minValue: -360,
		maxValue: 360,
		enableKeyEvents: true,
		listeners: {
			spin: function () {
				printExtent.page.setRotation(this.getValue(), true);
			},
			keyup: function (textField, event) {
				printExtent.page.setRotation(this.getValue(), true);
				event.stopPropagation();
			},
			keydown: function (textField, event) {
				event.stopPropagation();
			},
			keypress: function (textField, event) {
				event.stopPropagation();
			}
		}
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'button',
		flex: 1,
		tooltip: 'Print',
		text: 'Print',
		tooltipType: 'qtip',
		iconCls: '',
		scale: 'medium',
		listeners: {
			click: function () {
				var overlays_root = Ext.getCmp('layers-tree-panel').root.findChild('id', 'overlays-root');
				var params = {
					FORMAT: Ext.getCmp('print-format-combobox').getValue(),
					DPI: printExtent.printProvider.dpi.get("value"),
					TEMPLATE: printExtent.printProvider.layout.get("name"),
					LAYERS: overlays_root.getVisibleLayers().reverse().join(','),
					SRS: mappanel.map.projection.getCode(),
					'map0:extent': printExtent.page.getPrintExtent(mappanel.map).toBBOX(1, false),
					'map0:rotation': -printExtent.page.rotation,
					'map0:scale': printExtent.page.scale.get("value")
				}
				// labels
				var labels_data = Ext.getCmp('print-composer-labels-grid').getSource();
				for (label in labels_data) {
					params[label] = labels_data[label];
				}
				var printUrl = Ext.urlAppend('{% autoescape off %}{{ getprint_url }}{% endautoescape %}', Ext.urlEncode(params))
				window.open(printUrl, '_blank');
				//Ext.getCmp('print-action').toggle(false);
			}
		}
	}],
	items:[
		new Ext.grid.PropertyGrid({
			id: 'print-composer-labels-grid',
			region: 'center',
			hideHeaders: true,
			autoHeight: true,
			autoExpandColumn: 'Value',
			viewConfig : {
				forceFit: true,
				scrollOffset: 0
			}
		})
	]
});

action = new Ext.Action({
	id: 'print-action',
	map: mappanel.map,
	cls: 'x-btn-icon',
	iconCls: 'print-icon',
	enableToggle: true,
	toggleGroup: 'tools',
	tooltip: 'Print',
	toggleHandler: function(button, toggled) {
		if (toggled) {
			printWindow.show();
			printWindow.alignTo(mappanel.getTopToolbar().getId(), 'bl', [70, 4]);
		} else {
			printWindow.hide();
		}
	},
});
mappanel.getTopToolbar().add('-', action);
