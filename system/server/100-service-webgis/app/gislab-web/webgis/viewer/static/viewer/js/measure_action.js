Ext.namespace('WebGIS');

WebGIS.MeasureAction = Ext.extend(Ext.Action, {
	controls: null,
	window: null,
	unit2unit: {
		m: {m: 1, km: 0.001, mi: 0.00062137},
		km: {m: 1000, km: 1, mi: 0.62137},
		mi: {m: 1609.347088, km: 1.609347088, mi: 1},
		m2: {m2: 1, km2: 0.000001, ha: 0.0001, are: 0.01},
		km2: {m2: 1000000, km2: 1, ha: 100, are: 10000},
		ha: {m2: 10000, km2: 0.01, ha: 1, are: 100},
		are: {m2: 100, km2: 0.0001, ha: 0.01, are: 1}
	},

	constructor: function(config) {
		this.map = config.map;
		this.pointMeasureControl = config.pointMeasureControl;
		this.lengthMeasureControl = config.lengthMeasureControl;
		this.areaMeasureControl = config.areaMeasureControl;
		this.map.addControl(this.pointMeasureControl);
		this.map.addControl(this.lengthMeasureControl);
		this.map.addControl(this.areaMeasureControl);
		WebGIS.MeasureAction.superclass.constructor.apply(this, arguments);
	},

	convertUnits: function( value, from_units, to_units ) {
		return value * this.unit2unit[from_units][to_units];
	},
	onPointMeasure: function(evt) {
		this.measurePointPanel.pointForm.getForm().setValues({
			'coord1': evt.geometry.x,
			'coord2': evt.geometry.y
		});
	},
	onLengthMeasurePartial: function(evt) {
		var total_length = evt.measure;
		var units = evt.units;
		var geom = evt.geometry.clone();
		while(geom.components.length > 2) {
			geom.removeComponent(geom.components[0]);
		}
		var last_segment_data = this.lengthMeasureControl.getBestLength(geom);
		var last_segment_length = last_segment_data[0];
		var last_segment_units = last_segment_data[1];

		var dest_units = this.measureLengthPanel.lengthUnits.getValue();
		if (dest_units) {
			total_length = this.convertUnits(total_length, units, dest_units);
			last_segment_length = this.convertUnits(last_segment_length, last_segment_units, dest_units);
			units = dest_units;
			last_segment_units = dest_units;
		}
		this.measureLengthPanel.lengthForm.getForm().setValues({
			'total': total_length.toFixed(3)+' '+units,
			'last_segment': last_segment_length.toFixed(3)+' '+last_segment_units
		});
		this.measureLengthPanel.lastMeasurement = {
			total: {
				value: total_length,
				units: units
			},
			last_segment: {
				value: last_segment_length,
				units: last_segment_units
			}
		};
	},
	onAreaMeasurePartial: function(evt) {
		var area = evt.measure;
		var area_units = evt.units+'2';
		var area_dest_units = this.measureAreaPanel.areaUnits.getValue();
		if (area_dest_units) {
			area = this.convertUnits(area, area_units, area_dest_units);
			area_units = area_dest_units;
		}
		var perimeter_data = this.areaMeasureControl.getBestLength(evt.geometry);
		var perimeter = perimeter_data[0];
		var perimeter_units = perimeter_data[1];
		var perimeter_dest_units = this.measureAreaPanel.perimeterUnits.getValue();
		if (perimeter_dest_units) {
			perimeter = this.convertUnits(perimeter, perimeter_units, perimeter_dest_units);
			perimeter_units = perimeter_dest_units;
		}
		this.measureAreaPanel.lastMeasurement = {
			'area': {
				'value': area,
				'units': area_units
			},
			'perimeter': {
				'value': perimeter,
				'units': perimeter_units
			}
		}
		area_units = area_units.replace('2', '²');
		this.measureAreaPanel.areaForm.getForm().setValues({
			'area': area.toFixed(3)+' '+area_units,
			'perimeter': perimeter.toFixed(3)+' '+perimeter_units
		});
	},
	showMeasureToolbar: function() {
		if (this.window) {
			this.window.show();
			var activeTab = this.window.get(0).getActiveTab();
			activeTab.clearMeasurements();
			activeTab.control.activate();
			return;
		}
		this.measurePointPanel = new Ext.Panel({
			xtype: 'panel',
			title: gettext('Point'),
			autoScroll: true,
			cls: 'measure-panel',
			iconCls: 'measure-point-icon',
			control: this.pointMeasureControl,
			viewConfig: {
				forceFit: true,
			},
			layout: 'column',
			autoScroll: false,
			border: false,
			defaults: {
				border: false
			},
			items: [{
				title: gettext('Measured values'),
				columnWidth: 1,
				items: [{
						xtype: 'form',
						ref: '/pointForm',
						labelWidth: 100,
						frame: false,
						border: false,
						defaults: {
							anchor: "100%",
						},
						defaultType: 'textfield',
						items: [{
								fieldLabel: gettext('Coordinate 1'),
								name: 'coord1',
								readOnly: true,
								listeners: {
									focus: function(field) {
										field.selectText();
									}
								}
							}, {
								fieldLabel: gettext('Coordinate 2'),
								name: 'coord2',
								readOnly: true,
								listeners: {
									focus: function(field) {
										field.selectText();
									}
								}
							},
						]
				}]
			}],
			clearMeasurements: function() {
				this.pointForm.getForm().reset();
			}
		});
		this.measureLengthPanel = new Ext.Panel({
			xtype: 'panel',
			title: gettext('Length'),
			autoScroll: false,
			cls: 'measure-panel',
			iconCls: 'measure-line-icon',
			control: this.lengthMeasureControl,
			viewConfig: {
				forceFit: true,
			},
			layout: 'column',
			border: false,
			defaults: {
				border: false
			},
			items: [{
					title: gettext('Measured values'),
					columnWidth: .75,
					items: [{
						xtype: 'form',
						ref: '/lengthForm',
						labelWidth: 100,
						frame: false,
						border: false,
						defaults: {
							anchor: "100%",
						},
						defaultType: 'textfield',
						items: [
							{
								fieldLabel: gettext('Last segment'),
								name: 'last_segment',
								readOnly: true,
								listeners: {
									focus: function(field) {
										field.selectText();
									}
								}
							}, {
								fieldLabel: gettext('Total length'),
								name: 'total',
								readOnly: true,
								listeners: {
									focus: function(field) {
										field.selectText();
									}
								}
							}
						]
					}]
				}, {
					title: gettext('Units'),
					columnWidth: .25,
					items: [{
						xtype: 'form',
						labelWidth: 1,
						frame: false,
						border: false,
						defaults: {
							anchor: "100%",
						},
						items: [{
							xtype: 'box',
							height: 26,
						}, {
							xtype: 'combo',
							name: 'units',
							ref: '../../lengthUnits',
							store: new Ext.data.SimpleStore({
								data: [
									['', 'auto'],
									['m', 'm'],
									['km', 'km'],
									['mi', 'mi'],
								],
								id: 0,
								fields: ['value', 'display']
							}),
							valueField: 'value',
							displayField: 'display',
							mode: 'local',
							triggerAction: 'all',
							forceSelection: true,
							measureAction: this,
							listeners: {
								afterrender: function(combo) {
									var recordSelected = combo.getStore().getAt(0);
									combo.setValue(recordSelected.get('value'));
								},
								select: function (combo, record, index) {
									var units = record.get('value');
									if (units) {
										var last_measurement = combo.measureAction.measureLengthPanel.lastMeasurement;
										if (last_measurement) {
											var total_value = combo.measureAction.convertUnits(last_measurement['total']['value'], last_measurement['total']['units'], units);
											var last_segment_value = combo.measureAction.convertUnits(last_measurement['last_segment']['value'], last_measurement['last_segment']['units'], units);
											combo.measureAction.measureLengthPanel.lengthForm.getForm().setValues({
												'total': total_value.toFixed(3) +' '+units,
												'last_segment': last_segment_value.toFixed(3) +' '+units,
											});
										}
									} else {
										combo.setValue('');
									}
								}
							}
					}]
				}]
			}],
			clearMeasurements: function() {
				this.lengthForm.getForm().reset();
			}
		});
		this.measureAreaPanel = new Ext.Panel({
			xtype: 'panel',
			title: gettext('Area'),
			autoScroll: false,
			cls: 'measure-panel',
			iconCls: 'measure-polygon-icon',
			control: this.areaMeasureControl,
			viewConfig: {
				forceFit: true,
			},
			layout: 'column',
			border: false,
			defaults: {
				border: false
			},
			items: [{
				title: gettext('Measured values'),
				columnWidth: .75,
				items: [{
					xtype: 'form',
					ref: '/areaForm',
					labelWidth: 100,
					frame: false,
					border: false,
					defaults: {
						anchor: "100%",
					},
					defaultType: 'textfield',
					items: [
						{
							fieldLabel: gettext('Area'),
							name: 'area',
							readOnly: true,
							listeners: {
								focus: function(field) {
									field.selectText();
								}
							}
						}, {
							fieldLabel: gettext('Perimeter'),
							name: 'perimeter',
							readOnly: true,
							listeners: {
								focus: function(field) {
									field.selectText();
								}
							}
						}
					]
				}]
			}, {
				title: gettext('Units'),
				columnWidth: .25,
				items: [{
					xtype: 'form',
					labelWidth: 1,
					frame: false,
					border: false,
					defaults: {
						anchor: "100%",
					},
					items: [{
							xtype: 'combo',
							name: 'units',
							ref: '../../areaUnits',
							store: new Ext.data.SimpleStore({
								data: [
									['', 'auto'],
									['m2', 'm²'],
									['km2', 'km²'],
									['ha', 'ha'],
									['are', 'are']
								],
								id: 0,
								fields: ['value', 'display']
							}),
							valueField: 'value',
							displayField: 'display',
							mode: 'local',
							triggerAction: 'all',
							forceSelection: true,
							measureAction: this,
							listeners: {
								afterrender: function(combo) {
									var recordSelected = combo.getStore().getAt(0);
									combo.setValue(recordSelected.get('value'));
								},
								select: function (combo, record, index) {
									var units = record.get('value');
									if (units) {
										var last_measurement = combo.measureAction.measureAreaPanel.lastMeasurement;
										if (last_measurement) {
											var area_value = combo.measureAction.convertUnits(last_measurement['area']['value'], last_measurement['area']['units'], units);
											combo.measureAction.measureAreaPanel.areaForm.getForm().setValues({
												'area': area_value.toFixed(3) +' '+units,
											});
										}
									} else {
										combo.setValue('');
									}
								}
							}
						}, {
							xtype: 'combo',
							ref: '../../perimeterUnits',
							store: new Ext.data.SimpleStore({
								data: [
									['', 'auto'],
									['m', 'm'],
									['km', 'km'],
									['mi', 'mi'],
								],
								id: 0,
								fields: ['value', 'display']
							}),
							valueField: 'value',
							displayField: 'display',
							mode: 'local',
							triggerAction: 'all',
							forceSelection: true,
							measureAction: this,
							listeners: {
								afterrender: function(combo) {
									var recordSelected = combo.getStore().getAt(0);
									combo.setValue(recordSelected.get('value'));
								},
								select: function (combo, record, index) {
									var units = record.get('value');
									if (units) {
										var last_measurement = combo.measureAction.measureAreaPanel.lastMeasurement;
										if (last_measurement) {
											var perimeter_value = combo.measureAction.convertUnits(last_measurement['perimeter']['value'], last_measurement['perimeter']['units'], units);
											combo.measureAction.measureAreaPanel.areaForm.getForm().setValues({
												'perimeter': perimeter_value.toFixed(3) +' '+units,
											});
										}
									} else {
										combo.setValue('');
									}
								}
							}
						}
					]
				}]
			}],
			clearMeasurements: function() {
				this.areaForm.getForm().reset();
			}
		});
		this.pointMeasureControl.events.register('measure', this, this.onPointMeasure);
		this.lengthMeasureControl.events.register('measurepartial', this, this.onLengthMeasurePartial);
		this.areaMeasureControl.events.register('measurepartial', this, this.onAreaMeasurePartial);

		this.window = new Ext.Window({
			id: 'measure-window',
			header: false,
			closable: false,
			resizable: false,
			width: 400,
			layout: 'fit',
			items: [
				{
					xtype: 'tabpanel',
					activeTab: 0,
					items: [
						this.measurePointPanel,
						this.measureLengthPanel,
						this.measureAreaPanel
					],
					measureAction: this,
					listeners: {
						beforetabchange: function(tabPanel, newTab, currentTab) {
							if (currentTab) {
								currentTab.control.deactivate();
							}
							if (newTab) {
								newTab.clearMeasurements();
								newTab.control.activate();
							}
						},
					}
				}
			],
			listeners: {
				beforehide: function(window) {
					var activeTab = window.get(0).getActiveTab();
					activeTab.control.deactivate();
				}
			}
		});
		this.window.show();
		this.window.alignTo(Ext.getCmp('map-panel').getTopToolbar().getId(), 'tr-br', [-5, 0]);
	},

	toggleHandler: function(action, toggled) {
		if (toggled) {
			this.showMeasureToolbar();
		} else {
			if (this.window) {
				this.window.hide();
			}
		}
	}
});
