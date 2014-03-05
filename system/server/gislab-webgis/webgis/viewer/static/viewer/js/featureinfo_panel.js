Ext.namespace('WebGIS');

WebGIS.FeatureInfoPanel = Ext.extend(Ext.Panel, {
	title: 'Feature Info',
	split: true,
	map: null,
	layout: 'fit',
	autoPanMapOnSelection: false,
	styleMap: null,

	initComponent: function() {
		this.featureinfo_tabpanel = new Ext.TabPanel({
			id: 'featureinfo-tabpanel',
			items: [],
			listeners: {
				'tabchange': function (tabPanel, tab) {
					if (!tab) {
						return;
					}
					// deactivate features selection control on map
					if (tab.selModel.selectControl) {
						tab.selModel.selectControl.deactivate();
					}
					var tab_layer_name = '_featureinfolayer_' + tab.title;
					Ext.each(this.map.getLayersByName(new RegExp('^_featureinfolayer_.+')), function(layer) {
						layer.setVisibility(layer.name == tab_layer_name);
					});
				}
			}
		});
		if (this.styleMap == null) {
			this.styleMap = new OpenLayers.StyleMap({
				'default':{
					strokeColor: '#FFCC00',
					strokeOpacity: 0.6,
					strokeWidth: 2,
					fillColor: '#FFCC00',
					fillOpacity: 0.2,
					pointRadius: 6,
				},
				'select': {
					strokeColor: '#FF0000',
					strokeOpacity: 0.8,
					strokeWidth: 2,
					fillColor: '#FF0000',
					fillOpacity: 0.7,
					pointRadius: 6,
				}
			});
		}
		Ext.apply(this, {
			items: [this.featureinfo_tabpanel]
		});
		this.featureinfo_tabpanel.map = this.map;
		WebGIS.FeatureInfoPanel.superclass.initComponent.call(this);
	},

	clearFeaturesLayers: function() {
		this.featureinfo_tabpanel.removeAll(true);
		Ext.each(this.map.getLayersByName(new RegExp('^_featureinfolayer_.+')), function(layer) {
			layer.destroyFeatures();
			layer.setVisibility(false);
		});
	},

	showFeatures: function(features) {
		this.clearFeaturesLayers();
		var featureinfo_data = {};
		if (features.length > 0) {
			// split features by layer name
			Ext.each(features, function(feature) {
				var layer_name = feature.fid.split(".")[0];
				if (!featureinfo_data.hasOwnProperty(layer_name)) {
					featureinfo_data[layer_name] = [];
				}
				featureinfo_data[layer_name].push(feature);
			});

			// prepare feature attributes data for GridPanel separately for each layer
			for (var layer_name in featureinfo_data) {
				var layer_features = featureinfo_data[layer_name];

				// create vector layer for layer features if it does not already exist
				var features_layername = '_featureinfolayer_'+layer_name;
				var flayer = this.map.getLayer(features_layername);
				if (flayer == null) {
					flayer = new OpenLayers.Layer.Vector(features_layername, {
						eventListeners: {},
						styleMap: this.styleMap,
					});
					flayer.id = features_layername;
					flayer.displayInLayerSwitcher = false;
				}
				this.map.addLayer(flayer);

				// create header info of features attributes (of the same layer)
				var fields = [], columns = [], data = [];
				for (var attr_name in layer_features[0].attributes) {
					if (attr_name == 'geometry' || attr_name == 'boundedBy') {continue;}
					fields.push({ name: attr_name, type: 'string' });
					columns.push({id: attr_name, header: attr_name, dataIndex: attr_name});
				}

				var store = new GeoExt.data.FeatureStore({
					layer: flayer,
					fields: fields,
					features: layer_features,
					autoLoad: true
				});
				var grid_panel = new Ext.grid.GridPanel({
					title: layer_name,
					autoDestroy: true,
					store: store,
					autoExpandColumn: fields[fields.length-1].name,
					autoExpandMax: 2000,
					viewConfig: {
						templates: {
							cell: new Ext.Template(
								'<td class="x-grid3-col x-grid3-cell x-grid3-td-{id} x-selectable {css}" style="{style}" tabIndex="0" {cellAttr}>\
									<div class="x-grid3-cell-inner x-grid3-col-{id}" {attr}>{value}</div>\
								</td>'
							)
						}
					},
					cm: new Ext.grid.ColumnModel({
						defaults: {
							sortable: true
						},
						columns: columns
					}),
					sm: new GeoExt.grid.FeatureSelectionModel({
						autoPanMapOnSelection: this.autoPanMapOnSelection
					}),
					listeners: {
						'removed': function (grid, ownerCt ) {
							grid.selModel.unbind();
						}
					}
				});
				this.featureinfo_tabpanel.add(grid_panel);
			}
			this.expand(false);
			this.featureinfo_tabpanel.setActiveTab(0);
			this.featureinfo_tabpanel.doLayout();
		}
	},
	listeners: {
		collapse: function(panel) {
			this.clearFeaturesLayers();
		}
	},
});

