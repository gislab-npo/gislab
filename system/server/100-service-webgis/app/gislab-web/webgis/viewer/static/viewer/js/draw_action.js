Ext.namespace('WebGIS');

WebGIS.DrawAction = Ext.extend(Ext.Action, {
	dialogTitle: '',
	controls: null,
	snapping: false,
	saveHandler: function(drawAction, title, features) {},

	layers: null,
	window: null,
	snapControl: null,
	modifyControl: null,

	constructor: function(config) {
		if (config.hasOwnProperty('dialogTitle')) {
			this.dialogTitle = config.dialogTitle;
		}
		if (config.hasOwnProperty('saveHandler')) {
			this.saveHandler = config.saveHandler;
		}
		if (config.hasOwnProperty('snapping')) {
			this.snapping = config.snapping;
		}
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
		var currentTab = this.window.get(0).getActiveTab();
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
			mode: OpenLayers.Control.ModifyFeature.RESHAPE
		});
		this.map.addControl(this.modifyControl);
		this.modifyControl.activate();
		this.modifyControl.layer.events.register("featureselected", this, this.onFeatureSelected);
	},

	enableSnapping: function(draw_control) {
		this.disableSnapping();
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
	},

	showDrawingToolbar: function() {
		var features_editors = [];
		Ext.each(this.controls, function(control) {
			var store = new GeoExt.data.FeatureStore({
				layer: control.control.layer,
				fields: [
					{name: 'title', type: 'string'},
					{name: 'description', type: 'string'},
				],
			});
			var cm = new Ext.grid.ColumnModel({
				columns: [
					new Ext.grid.RowNumberer({
						width: 25
					}), {
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
						})
					}, {
						header: gettext('Description'),
						dataIndex: 'description',
						editor: new Ext.form.TextField({
							allowBlank: true,
							maxLength: 200,
							autoCreate : { //restricts user to 20 chars max
								tag: 'input',
								maxlength : 200,
								type: 'text',
								autocomplete: 'off'
							},
						})
					}
				]
			});
			var features_editor = new Ext.grid.EditorGridPanel({
				xtype: 'editorgrid',
				title: control.title,
				autoScroll: true,
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
				listeners: {
					'removed': function (grid, ownerCt) {
						grid.selModel.unbind();
					}
				},
			});
			features_editors.push(features_editor);
		}, this);

		if (!this.historyStore) {
			this.historyStore = new Ext.data.ArrayStore({
				fields: [
					{name: 'time', type: 'date'},
					{name: 'title', type: 'string'},
					{name: 'permalink', type: 'string'},
					{name: 'download', type: 'string'},
					{name: 'info', type: 'string'},
				]
			});
		}
		function tooltip_renderer(val, meta, record, rowIndex, colIndex, store) {
			var info = record.get('info');
			meta.attr = String.format('ext:qtip="{0}"',  info);
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
					width    : 60,
					sortable : false,
					dataIndex: 'time',
					renderer : Ext.util.Format.dateRenderer('H:i:s'),
				}, {
					id       : 'title',
					header   : gettext('Title'),
					sortable : false,
					dataIndex: 'title',
					renderer:  tooltip_renderer
				}, {
					id       : 'permalink',
					header   : gettext('Permalink'),
					width    : 72,
					sortable : false,
					dataIndex: 'permalink',
				}, {
					id       : 'permalink',
					header   : gettext('Download'),
					width    : 72,
					sortable : false,
					dataIndex: 'download',
				},

			],
			//stripeRows: true,
			autoExpandColumn: 'title',
			// config options for stateful behavior
			stateful: true,
			stateId: 'grid'
		});

		this.window = new Ext.Window({
			id: 'drawing-window',
			header: false,
			//title: this.dialogTitle,
			closable: false,
			minWidth: 300,
			width: 400,
			height: 400,
			layout: 'fit',
			tbar: {
				xtype: 'toolbar',
				dock: 'top',
				layout: {
					type: 'hbox',
					pack: 'start',
				},
				items: [{
						xtype: 'tbtext',
						text: gettext('Title')+':',
						flex: 0
					}, {
					xtype: 'tbspacer',
						width: 10
					}, {
						xtype: 'textfield',
						ref: '/drawingTitle',
						flex: 1
					}
				]
			},
			bbar: [
				'->', {
					xtype: 'tbbutton',
					text: gettext('Delete selected'),
					tooltip: gettext('Delete selected'),
					hideMode: 'visibility',
					drawAction: this,
					handler: function() {
						var features_editor = this.drawAction.window.get(0).activeTab;
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
				}, '-', {
					xtype: 'tbbutton',
					text: gettext('Delete all'),
					tooltip: gettext('Delete all'),
					hideMode: 'visibility',
					drawAction: this,
					handler: function() {
						var features_editor = this.drawAction.window.get(0).activeTab;
						features_editor.getStore().layer.destroyFeatures();
					}
				}, '-',
				new Ext.Action({
					cls: 'x-btn-text',
					text: gettext('Save'),
					tooltip: gettext('Save drawing'),
					hideMode: 'visibility',
					drawAction: this,
					handler: function(save_action) {
						var title = this.drawAction.window.drawingTitle.getValue();
						var features = [];
						var currentTab = this.drawAction.window.get(0).getActiveTab();
						this.drawAction.clearFeaturesSelection();
						Ext.each(this.drawAction.layers, function(layer) {
							features = features.concat(layer.features);
						});
						this.drawAction.saveHandler(this.drawAction, title, features);
					}
				})
			],
			items: [
				{
					xtype: 'tabpanel',
					activeTab: 0,
					items: features_editors.concat(history_grid),
					drawAction: this,
					listeners: {
						beforetabchange: function(tabPanel, newTab, currentTab) {
							if (currentTab && currentTab.control) {
								currentTab.control.deactivate();
								this.drawAction.clearFeaturesSelection();
							}
						},
						tabchange: function(tabPanel, tab) {
							if (tab && tab.control) {
								tab.control.setMap(this.drawAction.map);
								tab.control.activate();
								if (this.drawAction.snapping) {
									this.drawAction.disableSnapping();
									this.drawAction.enableSnapping(tab.control);
								}
								this.drawAction.enableFeatureModify(tab.control);
								this.drawAction.window.getBottomToolbar().items.each(function(item) {
									item.show();
								});
							} else { // history tab
								this.drawAction.window.getBottomToolbar().items.each(function(item) {
									item.hide();
								});
							}
						}
					}
				}
			],
			listeners: {
				beforehide: function(window) {
					var activeTab = window.get(0).getActiveTab();
					if (activeTab && activeTab.control) {
						activeTab.control.deactivate();
						activeTab.selModel.clearSelections();
					}
				}
			}
		});
		this.window.show();
		this.window.alignTo(Ext.getBody(), 'r-r', [-20, 0]);
	},

	toggleHandler: function(action, toggled) {
		if (toggled) {
			this.showDrawingToolbar();
		} else {
			if (this.snapping) {
				this.disableSnapping();
			}
			this.clearFeatureModifyControl();
			if (this.window) {
				this.window.destroy();
				this.window = null;
			}
		}
	},
});
