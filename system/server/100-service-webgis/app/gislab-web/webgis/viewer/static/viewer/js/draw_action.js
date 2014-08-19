Ext.namespace('WebGIS');

// prevent automatic scrolling to top
Ext.override(Ext.grid.GridView, {
	scrollToTop: Ext.emptyFn
});

WebGIS.DrawingsLocalStorageProxy = Ext.extend(Ext.data.MemoryProxy, {

	memoryDrawings: [],
	constructor: function(config) {
		this.storagePrefix = config.storagePrefix;
		WebGIS.DrawingsLocalStorageProxy.superclass.constructor.apply(this, arguments);
		this.hasPersistentStorage = typeof(Storage) !== "undefined";
		this.on('beforeload', this.loadPageRecords);
	},
	saveRecord: function(record) {
		if (this.hasPersistentStorage) {
			var encoded_record = [
				parseInt(record.time.getTime()/1000),
				record.title,
				record.permalink,
				record.drawing,
				record.statistics].join(";");

			var count_key = String.format('{0}-drawings-count', this.storagePrefix);
			var count = parseInt(localStorage.getItem(count_key)) || 0;
			var storage_key = String.format('{0}-drawing-{1}', this.storagePrefix, count);
			localStorage.setItem(storage_key, encoded_record);
			count++;
			localStorage.setItem(count_key, count);
		} else {
			record.time = parseInt(record.time.getTime()/1000);
			this.memoryDrawings.unshift(record);
		}
	},
	loadPageRecords: function(proxy, params) {
		if (this.hasPersistentStorage) {
			var count_key = String.format('{0}-drawings-count', this.storagePrefix);
			var count = parseInt(localStorage.getItem(count_key)) || 0;
			var drawings = [];
			if (count > 0) {
				for (var index = params.start; index < params.start+params.limit && index < count; index++) {
					var record_key = String.format('{0}-drawing-{1}', proxy.storagePrefix, count-index-1); // fetch in reversed order
					var encoded_record = localStorage.getItem(record_key);
					if (encoded_record) {
						var record_data = encoded_record.split(";");
						drawings.push({
							time: parseInt(record_data[0]),
							title: record_data[1],
							permalink: record_data[2],
							drawing: record_data[3],
							statistics: record_data[4]
						});
					}
				}
			}
			proxy.data = {
				count: count,
				drawings: drawings
			};
		} else {
			proxy.data = {
				count: this.memoryDrawings.length,
				drawings: this.memoryDrawings.slice(params.start, params.start+params.limit)
			};
		}
	}
});

WebGIS.DrawingsHttpProxy = Ext.extend(Ext.data.HttpProxy, {
	constructor: function(config) {
		this.user = config.user;
		this.project = config.project;
		config.method = 'GET';
		WebGIS.DrawingsHttpProxy.superclass.constructor.apply(this, arguments);
	},
	saveRecord: function(record) {
		Ext.Ajax.request({
			method: 'POST',
			url: this.url,
			params: {
				user: this.user,
				project: this.project,
				title: record.title,
				ball: record.drawing,
				permalink: record.permalink,
				statistics: record.statistics
			}
		});
	}
});

WebGIS.DrawAction = Ext.extend(Ext.Action, {
	controls: null,
	saveHandler: function(drawAction, title, features) {},
	drawingsHistoryProxy: null,

	layers: null,
	window: null,
	snapControl: null,
	modifyControl: null,
	isSnappingActivated: false,
	isSelectModeActivated: false,

	constructor: function(config) {
		if (config.saveHandler) {
			this.saveHandler = config.saveHandler;
		}
		if (config.drawingsHistoryProxy) {
			this.drawingsHistoryProxy = config.drawingsHistoryProxy;
		}
		this.drawingUrl = config.drawingUrl;
		this.controls = config.controls;
		this.controls[0].control.deactivate();
		this.map = config.map;
		var layers = [];
		Ext.each(this.controls, function(draw_control) {
			layers.push(draw_control.control.layer);
		});
		this.layers = layers;
		WebGIS.DrawAction.superclass.constructor.apply(this, arguments);
	},

	onFeatureSelected: function(evt) {
		var feature = evt.feature;
		this.modifyControl.selectFeature(feature);
	},
	clearFeaturesSelection: function() {
		var currentTab = this.window.drawPanel.getActiveTab();
		currentTab.selModel.clearSelections();
		if (this.modifyControl) {
			var modifyFeature = this.modifyControl.feature;
			if (modifyFeature) {
				this.modifyControl.unselectFeature(modifyFeature);
			}
		}
	},
	clearFeatureModifyControl: function() {
		if (this.modifyControl) {
			if (this.modifyControl.layer) {
				this.modifyControl.layer.events.unregister("featureselected", this, this.onFeatureSelected);
			}
			this.map.removeControl(this.modifyControl);
			this.modifyControl.deactivate();
			this.modifyControl.destroy();
		}
		this.modifyControl = null;
	},
	enableFeatureModify: function(draw_control) {
		this.clearFeatureModifyControl();
		this.modifyControl = new OpenLayers.Control.ModifyFeature(draw_control.layer, {
			standalone: true,
			vertexRenderIntent: 'modify',
			mode: OpenLayers.Control.ModifyFeature.RESHAPE,
			/*
			beforeSelectFeature: function(feature) {
				var grid = Ext.getCmp('drawing-window').drawPanel.activeTab;
				grid.getSelectionModel().selectRecords([grid.store.getByFeature(feature)]);
			},*/
			handleKeypress: function(evt) {
				var code = evt.keyCode;
				// check for delete key
				if(this.feature && OpenLayers.Util.indexOf(this.deleteCodes, code) != -1) {
					var vertex = this.layer.getFeatureFromEvent(this.handlers.drag.evt);
					if (evt.shiftKey && vertex &&
						OpenLayers.Util.indexOf(this.vertices, vertex) != -1 &&
						!this.handlers.drag.dragging && vertex.geometry.parent) {
						// remove the vertex
						vertex.geometry.parent.removeComponent(vertex.geometry);
						this.layer.events.triggerEvent("vertexremoved", {
							vertex: vertex.geometry,
							feature: this.feature,
							pixel: evt.xy
						});
						this.layer.drawFeature(this.feature, this.standalone ? undefined : 'select');
						this.modified = true;
						this.resetVertices();
						this.setFeatureState();
						this.onModification(this.feature);
						this.layer.events.triggerEvent("featuremodified", {feature: this.feature});
					} else if (!evt.shiftKey) {
						var feature = this.feature;
						var layer = feature.layer;
						this.unselectFeature(feature);
						layer.destroyFeatures(feature);
					}
				}
			}
		});
		this.map.addControl(this.modifyControl);
		this.modifyControl.activate();
		this.modifyControl.layer.events.register("featureselected", this, this.onFeatureSelected);
	},

	enableSnapping: function() {
		var draw_control = this.window.drawPanel.activeTab.control;
		if (this.isSnappingActivated) {
			this.disableSnapping();
		}
		this.isSnappingActivated = true;
		// configure the snapping agent
		this.snapControl = new OpenLayers.Control.Snapping({
			layer: draw_control.layer,
			defaults: {
				edge: false
			},
			targets: this.layers,
			greedy: false
		});
		this.snapControl.activate();
	},

	disableSnapping: function() {
		if (this.snapControl) {
			this.snapControl.deactivate();
			this.snapControl.destroy()
			this.snapControl = null;
		}
		this.isSnappingActivated = false;
	},

	showDrawingToolbar: function() {
		if (this.window) {
			this.window.show();
			return;
		}
		var features_editors = [];
		Ext.each(this.controls, function(control) {
			var store = new GeoExt.data.FeatureStore({
				layer: control.control.layer,
				drawAction: this,
				fields: [
					{name: 'title', type: 'string'},
					{name: 'description', type: 'string'},
				],
				listeners: {
					load: function(store, records, options) {
						// scroll to last item
						if (this.drawAction.window && this.getCount() > 5) {
							this.drawAction.window.drawPanel.activeTab.getView().focusRow(this.getCount()-1);
						}
					}
				}
			});
			function measurement_tooltip_renderer(val, meta, record, rowIndex, colIndex, store) {
				var info = '';
				var feature = record.get('feature');
				var mc = feature.layer.map.getControlsByClass('OpenLayers.Control.Measure')[0];
				if (feature.geometry.CLASS_NAME === 'OpenLayers.Geometry.Point') {
					info = String.format('{0}: {1} {2}', gettext('Coordinates'), feature.geometry.x, feature.geometry.y);
				} else if (feature.geometry.CLASS_NAME === 'OpenLayers.Geometry.LineString') {
					var length_data = mc.getBestLength(feature.geometry);
					info = String.format('{0}: {1} {2}', gettext('Length'), length_data[0].toFixed(3), length_data[1]);
				} else if (feature.geometry.CLASS_NAME === 'OpenLayers.Geometry.Polygon') {
					var area_data = mc.getBestArea(feature.geometry);
					var perimeter_data = mc.getBestLength(feature.geometry);
					info = String.format('{0}: {1} {2}<sup>2</sup><br />{3}: {4} {5}',
						gettext('Area'), area_data[0].toFixed(3), area_data[1],
						gettext('Perimeter'), perimeter_data[0].toFixed(3), perimeter_data[1]);
				}
				meta.attr = String.format('ext:qtip="{0}"',  info);
				return val;
			};
			var cm = new Ext.grid.ColumnModel({
				defaults: {
					sortable: false,
					menuDisabled: true,
				},
				columns: [
					{
						xtype : 'actioncolumn',
						width: 16,
						scope: this,
						hideable: false,
						resizable: false,
						items : [{
							tooltip : gettext('Zoom to feature'),
							getClass: function(v, meta, rec) {
								return 'zoom-to-feature';
							},
							handler: function(grid, rowIndex, colIndex) {
								grid.getSelectionModel().selectRow(rowIndex);
								var feature = grid.getStore().getAt(rowIndex).get('feature');
								if (feature.geometry.CLASS_NAME === 'OpenLayers.Geometry.Point') {
									this.map.setCenter(feature.geometry.bounds.getCenterLonLat());
								} else {
									this.map.zoomToExtent(feature.geometry.bounds, true);
								}
							}
						}],
					}, {
						header: gettext('Title'),
						dataIndex: 'title',
						width: 50,
						editor: new Ext.form.TextField({
							allowBlank: true,
							maxLength: 70,
							autoCreate : { //restricts user to 20 chars max
								tag: 'input',
								maxlength : 50,
								type: 'text',
								autocomplete: 'off'
							},
						}),
						renderer:  measurement_tooltip_renderer
					}, {
						header: gettext('Description'),
						dataIndex: 'description',
						menuDisabled: true,
						editor: new Ext.form.TextField({
							allowBlank: true,
							maxLength: 200,
							autoCreate : { //restricts user to 20 chars max
								tag: 'input',
								maxlength : 200,
								type: 'text',
								autocomplete: 'off'
							},
						}),
						renderer:  measurement_tooltip_renderer
					}
				]
			});
			var features_editor = new Ext.grid.EditorGridPanel({
				xtype: 'editorgrid',
				title: control.title,
				autoScroll: true,
				trackMouseOver: true,
				viewConfig: {
					forceFit:true,
				},
				autoExpandColumn: 'description',
				iconCls: control.iconCls,
				control: control.control,
				store: store,
				cm: cm,
				sm: new GeoExt.grid.FeatureSelectionModel({
					singleSelect: true,
					multiple: false,
					layerFromStore: true
				}),
			bbar: [
				new Ext.Action({
					ref: '/selectMode',
					iconCls: 'select-mode-icon',
					pressed: false,
					enableToggle: true,
					scope: this,
					toggleHandler: function(action, toggled) {
						var draw_control = this.window.drawPanel.activeTab.control;
						if (toggled) {
							draw_control.deactivate();
						} else {
							draw_control.activate();
						}
						this.isSelectModeActivated = toggled;
					}
				}), ' ', new Ext.Action({
					ref: '/snapAction',
					iconCls: 'snapping-icon',
					enableToggle: true,
					pressed: false,
					scope: this,
					toggleHandler: function(action, toggled) {
						if (toggled) {
							this.enableSnapping();
						} else {
							this.disableSnapping();
						}
					}
				}), '->', {
					xtype: 'tbbutton',
					ref: '/deleteSelected',
					text: gettext('Delete selected'),
					tooltip: gettext('Delete selected'),
					hideMode: 'visibility',
					drawAction: this,
					handler: function() {
						var features_editor = this.drawAction.window.drawPanel.activeTab;
						var layer = features_editor.getStore().layer;
						// copy selected features
						var selected_features = layer.selectedFeatures.slice(0);
						if (selected_features.length > 0) {
							this.drawAction.clearFeaturesSelection();
							layer.destroyFeatures(selected_features[0]);
						}
						// update row numbers
						features_editor.getView().refresh();
					}
				}, ' ', {
					xtype: 'tbbutton',
					text: gettext('Delete all'),
					tooltip: gettext('Delete all'),
					hideMode: 'visibility',
					drawAction: this,
					handler: function() {
						var features_editor = this.drawAction.window.drawPanel.activeTab;
						features_editor.getStore().layer.destroyFeatures();
					}
				}, ' ', new Ext.Action({
					cls: 'x-btn-text',
					text: gettext('Save'),
					tooltip: gettext('Save drawing'),
					hideMode: 'visibility',
					drawAction: this,
					handler: function(save_action) {
						var save_window = new Ext.Window({
							id: 'drawing-save-window',
							header: false,
							closable: false,
							modal: true,
							width: 450,
							height: 110,
							layout: 'fit',
							buttonAlign: 'right',
							scope: save_action,
							items: [{
									xtype: 'form',
									region: 'center',
									cls: 'save-drawings-form',
									labelWidth: 80,
									frame: true,
									defaults: {
										anchor: "100%",
									},
									defaultType: 'textfield',
									items: [{
											fieldLabel: gettext('Title'),
											name: 'title',
											ref: '/titleField',
											allowBlank: false,
											listeners: {
												afterrender: function(field) {
													field.focus(false, 200);
												}
											}
									}]
								}
							],
							buttons: [{
									text: gettext('Cancel'),
									scope: save_action,
									handler: function(button, evt) {
										var window = button.ownerCt.ownerCt;
										window.close();
									}
								}, {
									ref: '/save',
									text: gettext('Save'),
									scope: save_action,
									handler: function(button, evt) {
										var window = button.ownerCt.ownerCt;
										if (window.titleField.validate()) {
											var title = window.titleField.getValue();
											var features = [];
											var currentTab = this.drawAction.window.drawPanel.getActiveTab();
											this.drawAction.clearFeaturesSelection();
											Ext.each(this.drawAction.layers, function(layer) {
												features = features.concat(layer.features);
											});
											this.drawAction.saveHandler(this.drawAction, title, features);
											window.close();
										}
									}
							}],
							listeners: {
								render: function(window) {
									var map = new Ext.KeyMap(window.getEl(), [
										{
											key: [10, 13],
											fn: function() {
												window.save.handler.call(window.save.scope, window.save, Ext.EventObject);
											}
										}
									]);
								}
							}
						});
						save_window.show();
					}
				})
			],
			});
			features_editors.push(features_editor);
		}, this);

		this.historyStore = new Ext.data.JsonStore({
			drawAction: this,
			fields: [
				{
					name: 'time',
					type: 'date',
					convert: function(v) {
						return new Date(1000*parseInt(v));
					}
				}, {
					name: 'title',
					type: 'string'
				}, {
					name: 'permalink',
					type: 'string',
					convert: function(v) {
						return String.format('<a target="_blank" href="?{0}">{1}</a>', v, Ext.urlDecode(v)['DRAWINGS']);
					}
				}, {
					name: 'drawing',
					type: 'string',
					drawingUrl: this.drawingUrl,
					convert: function(v) {
						var link = Ext.urlAppend(this.drawingUrl, Ext.urlEncode({ID: v}));
						return String.format('<a target="_blank" href="{0}">{1}</a>', link, gettext('Download'));
					}
				}, {
					name: 'statistics',
					type: 'string'
				},
			],
			proxy: this.drawingsHistoryProxy,
			totalProperty: 'count',
			root: 'drawings',
		});

		function tooltip_renderer(val, meta, record, rowIndex, colIndex, store) {
			var statistics = record.get('statistics');
			meta.attr = String.format('ext:qtip="{0}"',  statistics);
			return val;
		};
		var history_grid = new Ext.grid.GridPanel({
			id: 'save-history-grid',
			title: gettext('History'),
			store: this.historyStore,
			viewConfig: {
				templates: {
					cell: new Ext.Template(
						'<td class="x-grid3-col x-grid3-cell x-grid3-td-{id} x-selectable {css}" style="{style}" tabIndex="0" {cellAttr}>\
							<div class="x-grid3-cell-inner x-grid3-col-{id}" {attr}>{value}</div>\
						</td>'
					)
				}
			},
			columns: [{
					id       : 'time',
					header   : gettext('Time'),
					dataIndex: 'time',
					width    : 82,
					sortable : false,
					menuDisabled: true,
					renderer : Ext.util.Format.dateRenderer('H:i d/m/y'),
				}, {
					id       : 'title',
					header   : gettext('Title'),
					dataIndex: 'title',
					sortable : false,
					menuDisabled: true,
					renderer:  tooltip_renderer
				}, {
					id       : 'permalink',
					header   : gettext('Permalink'),
					dataIndex: 'permalink',
					width    : 72,
					sortable : false,
					menuDisabled: true,
				}, {
					id       : 'drawing',
					header   : gettext('Download'),
					dataIndex: 'drawing',
					width    : 72,
					sortable : false,
					menuDisabled: true,
				},

			],
			//stripeRows: true,
			autoExpandColumn: 'title',
			// config options for stateful behavior
			stateful: true,
			stateId: 'grid',
			bbar: new Ext.PagingToolbar({
				store: this.historyStore,
				pageSize: 20,
				displayInfo: true,
				displayMsg: gettext('Drawings {0} - {1} of {2}'),
				emptyMsg: gettext('No drawings to display'),
			})
		});

		this.window = new Ext.Window({
			id: 'drawing-window',
			header: false,
			closable: false,
			minWidth: 300,
			width: 400,
			height: 400,
			layout: 'border',
			xtbar: {
				xtype: 'toolbar',
				dock: 'top',
				layout: {
					type: 'hbox',
					pack: 'start',
				},
				items: [{
						xtype: 'tbtext',
						text: gettext('Title')+':',
						hideMode: 'visibility',
						flex: 0
					}, {
						xtype: 'tbspacer',
						width: 10
					}, {
						xtype: 'textfield',
						ref: '/drawingTitle',
						hideMode: 'visibility',
						flex: 1
					}
				]
			},
			items: [
				{
					xtype: 'tabpanel',
					ref: 'drawPanel',
					activeTab: 0,
					region: 'center',
					items: features_editors.concat(history_grid),
					drawAction: this,
					initDrawTool: function() {
						var draw_control = this.drawAction.window.drawPanel.activeTab.control;
						draw_control.setMap(this.drawAction.map);
						// sync select mode and snapping tools with previous drawing geometry type settings (drawing tab)
						if (this.drawAction.isSelectModeActivated === this.drawAction.window.drawPanel.activeTab.selectMode.pressed) {
							if (!this.drawAction.isSelectModeActivated) {
								draw_control.activate();
							}
						} else {
							this.drawAction.window.drawPanel.activeTab.selectMode.toggle(this.drawAction.isSelectModeActivated);
						}
						this.drawAction.window.drawPanel.activeTab.snapAction.toggle(this.drawAction.isSnappingActivated);
						if (this.drawAction.isSnappingActivated) {
							this.drawAction.enableSnapping();
						} else {
							this.drawAction.disableSnapping();
						}
						this.drawAction.enableFeatureModify(draw_control);
					},
					listeners: {
						beforetabchange: function(tabPanel, newTab, currentTab) {
							if (currentTab && currentTab.control) {
								currentTab.control.deactivate();
								this.drawAction.clearFeaturesSelection();
							}
						},
						tabchange: function(tabPanel, tab) {
							if (tab && tab.control) {
								tabPanel.initDrawTool();
							} else { // history tab
								tab.getBottomToolbar().doRefresh();
							}
						}
					}
				}
			],
			listeners: {
				beforehide: function(window) {
					var activeTab = window.drawPanel.getActiveTab();
					if (activeTab && activeTab.control) {
						activeTab.control.deactivate();
						activeTab.selModel.clearSelections();
					}
				},
				show: function(window) {
					window.drawPanel.initDrawTool();
				}
			}
		});
		this.window.show();
		this.window.alignTo(Ext.getCmp('map-panel').getTopToolbar().getId(), 'tr-br', [-5, 5]);
	},

	toggleHandler: function(action, toggled) {
		if (toggled) {
			this.showDrawingToolbar();
		} else {
			this.clearFeatureModifyControl();
			if (this.window) {
				this.window.hide();
			}
		}
	}
});
