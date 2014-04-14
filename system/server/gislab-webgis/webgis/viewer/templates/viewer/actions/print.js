//Print Action
var printWindow = new Ext.Window({
	id: 'print-toolbar-window',
	autoHeight: true,
	layout: 'fit',
	resizable: false,
	closable: false,
	listeners: {
		hide: function(window) {
			printExtent.map.events.unregister("zoomend", this, this.updatePrintScales);
			printExtent.hide();
		},
		show: function(window) {
			this.updatePrintScales();
			//printExtent.page.setRotation(0, true);
			printExtent.page.setCenter(printExtent.map.getCenter());
			printExtent.map.events.register("zoomend", this, this.updatePrintScales);
			printExtent.page.on('change', function(window, mods) {
				if (mods.hasOwnProperty('rotation')) {
					var spinner = window.rotationSpinner;
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
		var map_scale = Math.round(printExtent.map.getScale());
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
	tbar: [
		{
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

					var window = combo.ownerCt.ownerCt;
					window.removeAll();
					if (layout.json.labels.length > 0) {
						var form_fields = [];
						Ext.each(layout.json.labels, function(label) {
							form_fields.push({
								fieldLabel: label,
								name: label,
								allowBlank: true
							});
						});
						window.add({
							xtype: 'form',
							labelWidth: 100,
							frame: true,
							defaults: {
								anchor: "100%",
							},
							autoHeight: true,
							defaultType: 'textfield',
							items: form_fields,
						});
					}
					if (window.isVisible()) {
						window.doLayout();
					}
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
			ref: '/formatCombobox',
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
			ref: '/rotationSpinner',
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
		}, new Ext.Action({
			text: 'Print',
			tooltip: 'Print',
			tooltipType: 'qtip',
			flex: 1,
			iconCls: '',
			handler: function(action) {
				var print_window = Ext.getCmp('print-toolbar-window');
				var overlays_root = Ext.getCmp('layers-tree-panel').root;
				var params = {
					SERVICE: 'WMS',
					REQUEST: 'GetPrint',
					FORMAT: print_window.formatCombobox.getValue(),
					DPI: printExtent.printProvider.dpi.get("value"),
					TEMPLATE: printExtent.printProvider.layout.get("name"),
					LAYERS: overlays_root.getVisibleLayers().reverse().join(','),
					SRS: printExtent.map.projection.getCode(),
					'map0:extent': printExtent.page.getPrintExtent(printExtent.map).toBBOX(1, false),
					'map0:rotation': -printExtent.page.rotation,
					'map0:scale': printExtent.page.scale.get("value")
				}
				// labels
				if (print_window.items.length > 0) {
					var labels_data = print_window.get(0).getForm().getValues();
					for (label in labels_data) {
						params[label] = labels_data[label];
					}
				}

				var printUrl = Ext.urlAppend('{% autoescape off %}{{ ows_url }}{% endautoescape %}', Ext.urlEncode(params))
				window.open(printUrl, '_blank');
				//action.toggle(false);
			}
		})
	],
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
mappanel.getTopToolbar().add(action);
