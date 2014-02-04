Ext.namespace('WebGIS');

WebGIS.DrawAction = Ext.extend(GeoExt.Action, {
	dialogTitle: '',
	snapping: false,
	snappingLayerTargets: [],

	attributes_window: null,
	snap_control: null,
	modify_control: null,

	constructor: function(config) {
		if (config.hasOwnProperty('dialogTitle')) {
			this.dialogTitle = config.dialogTitle;
		}
		if (config.hasOwnProperty('snappingLayerTargets')) {
			this.snappingLayerTargets = config.snappingLayerTargets;
		}
		this.map = config.map;
		this.snapping = this.snappingLayerTargets.length > 0;
		WebGIS.DrawAction.superclass.constructor.apply(this, arguments);
	},

	enableFeatureModify: function() {
		function onFeatureSelected(evt) {
			var feature = evt.feature;
			if (this.modify_control) {
				this.modify_control.deactivate();
				this.modify_control.destroy();
			}
			this.modify_control = new OpenLayers.Control.ModifyFeature(this.control.layer, {
				standalone: true,
				vertexRenderIntent: 'modify',
				mode: OpenLayers.Control.ModifyFeature.RESHAPE
			});
			this.modify_control.setMap(this.map);
			this.modify_control.activate();
			this.modify_control.selectFeature(feature);
		}
		this.control.layer.events.register("featureselected", this, onFeatureSelected);
	},

	enableSnapping: function() {
		this.disableSnapping();
		// configure the snapping agent
		this.snap_control = new OpenLayers.Control.Snapping({
			layer: this.control.layer,
			defaults: {
				edge: false
			},
			targets: this.snappingLayerTargets,
			greedy: false
		});
		this.snap_control.activate();
	},

	disableSnapping: function() {
		if (this.snap_control) {
			this.snap_control.deactivate();
			this.snap_control.destroy()
			this.snap_control = null;
		}
	},

	showAttributesTable: function() {
		var store = new GeoExt.data.FeatureStore({
			layer: this.control.layer,
			fields: [{name: 'label', type: 'string'}],
		});
		var cm = new Ext.grid.ColumnModel({
			columns: [{
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
			}]
		})
		var features_editor = new Ext.grid.EditorGridPanel({
			autoScroll: true,
			viewConfig: {
				forceFit:true,
			},
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
					handler: function() {
						var selected_features = store.layer.selectedFeatures;
						if (selected_features.length > 0) {
							store.layer.destroyFeatures(selected_features[0]);
						}
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
		this.attribs_window = new Ext.Window({
			title: this.dialogTitle,
			width: 300,
			height: 400,
			layout: 'fit',
			items: [features_editor]
		});
		this.attribs_window.show();
		this.attribs_window.alignTo(Ext.getBody(), 'r-r', [-100, 0]);
	},

	toggleHandler: function(action, toggled) {
		if (toggled) {
			if (this.snapping) {
				this.enableSnapping();
			}
			this.enableFeatureModify();
			this.showAttributesTable();
		} else {
			if (this.snapping) {
				this.disableSnapping();
			}
			if (this.modify_control) {
				this.modify_control.deactivate();
				this.modify_control.destroy();
			}
			if (this.control.layer.selectedFeatures.length > 0) {
				new OpenLayers.Control.SelectFeature(this.control.layer).unselectAll();
			}
			if (this.attribs_window) {
				this.attribs_window.destroy();
				this.attribs_window = null;
			}
		}
	},
});
