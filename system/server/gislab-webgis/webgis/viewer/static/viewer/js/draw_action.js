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
		this.modifyControl.setMap(this.map);
		this.modifyControl.activate();
		draw_control.layer.events.register("featureselected", this, this.onFeatureSelected);
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
				fields: [{name: 'label', type: 'string'}],
			});
			var cm = new Ext.grid.ColumnModel({
				columns: [
					new Ext.grid.RowNumberer({
						width: 25
					}), {
						header: 'Label',
						dataIndex: 'label',
						editor: new Ext.form.TextField({
							allowBlank: true,
							maxLength: 50,
							autoCreate : { //restricts user to 20 chars max
								tag: 'input',
								maxlength : 50,
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
				bbar:[
					'->',
					{
						xtype: 'tbbutton',
						text: 'Delete selected',
						tooltip: 'Delete selected',
						drawAction: this,
						handler: function() {
							// copy selected features
							var selected_features = store.layer.selectedFeatures.slice(0);
							if (selected_features.length > 0) {
								this.drawAction.clearFeaturesSelection();
								store.layer.destroyFeatures(selected_features[0]);
							}
							// update row numbers
							this.ownerCt.ownerCt.getView().refresh();
						}
					},
					'-',
					 {
						xtype: 'tbbutton',
						text: 'Delete all',
						tooltip: 'Delete selected',
						handler: function() {
							store.layer.destroyFeatures();
						}
					}
				]
			});
			features_editors.push(features_editor);
		}, this);
		this.window = new Ext.Window({
			id: 'drawing-window',
			header: false,
			//title: this.dialogTitle,
			closable: false,
			minWidth: 300,
			width: 300,
			height: 400,
			layout: 'fit',
			tbar: [
				{
					xtype: 'label',
					text: 'Title:',
				}, {
					xtype: 'tbspacer',
					width: 10
				}, {
					xtype: 'textfield',
					width: 200,
					ref: '/drawingTitle',
				}, '->', new Ext.Action({
					cls: 'x-btn-text',
					text: 'Save',
					tooltip: 'Save drawing',
					drawAction: this,
					//toggleGroup: 'tools', // to disable drawing tools that could cause to export control points of OpenLayers.Control.ModifyFeature tool
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
					items: features_editors,
					drawAction: this,
					listeners: {
						beforetabchange: function(tabPanel, newTab, currentTab) {
							if (currentTab) {
								currentTab.control.deactivate();
								this.drawAction.clearFeaturesSelection();
							}
							if (newTab) {
								newTab.control.setMap(this.drawAction.map);
								//this.drawAction.control = tab.control;
								newTab.control.activate();
								if (this.drawAction.snapping) {
									this.drawAction.disableSnapping();
									this.drawAction.enableSnapping(newTab.control);
								}
								this.drawAction.enableFeatureModify(newTab.control);
							}
						},
					}
				}
			],
			listeners: {
				beforehide: function(window) {
					var activeTab = window.get(0).getActiveTab();
					if (activeTab) {
						activeTab.control.deactivate();
						activeTab.selModel.clearSelections();
					}
				}
			}
		});
		this.window.show();
		this.window.alignTo(Ext.getBody(), 'r-r', [-100, 0]);
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
