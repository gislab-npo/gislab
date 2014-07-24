Ext.namespace('WebGIS');

WebGIS.FeatureInfoPanel = Ext.extend(Ext.Panel, {
	split: true,
	map: null,
	layout: 'fit',
	autoPanMapOnSelection: false,
	styleMap: null,

	initComponent: function() {
		this.on('render', function(panel) {
			this.header.insertHtml('beforeEnd', '<span id="featureinfo-status"></span>');
			this.statusElem = Ext.get("featureinfo-status");
		});
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

	setStatusInfo: function(info) {
		this.statusElem.update(info);
	},

	setLayersMetadata: function(layers_meta) {
		this.layersMetadata = layers_meta;
	},

	clearFeaturesLayers: function() {
		this.featureinfo_tabpanel.removeAll(true);
		Ext.each(this.map.getLayersByName(new RegExp('^_featureinfolayer_.+')), function(layer) {
			layer.destroyFeatures();
			layer.setVisibility(false);
		});
		this.setStatusInfo('');
	},

	setFeaturesLayersVisibility: function(visibility) {
		Ext.each(this.map.getLayersByName(new RegExp('^_featureinfolayer_.+')), function(layer) {
			layer.setVisibility(visibility);
		});
	},

	showFeatures: function(features) {
		this.clearFeaturesLayers();
		var status_format = gettext('Number of results: %(count)s');
		this.setStatusInfo(interpolate(status_format, {"count": features.length}, true));
		var featureinfo_data = {};
		if (features.length > 0) {
			// split features by layer name
			Ext.each(features, function(feature) {
				var layer_name = feature.fid.substring(0, feature.fid.lastIndexOf("."));
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
				var fields = [];
				var columns = [];
				var data = [];
				if (layer_features[0].geometry) {
					columns.push({
						xtype : 'actioncolumn',
						width: 52,
						scope: this,
						sortable: false,
						hideable: false,
						resizable: false,
						menuDisabled: true,
						items : [{
							tooltip : gettext('Zoom to feature'),
							getClass: function(v, meta, rec) {
								return 'zoom-to-feature';
							},
							handler: function(grid, rowIndex, colIndex) {
								grid.getSelectionModel().selectRow(rowIndex);
								var feature = grid.getStore().getAt(rowIndex).get('feature'); //grid.getSelectionModel().selectedFeatures[0];
								if (feature.geometry.CLASS_NAME == 'OpenLayers.Geometry.Point') {
									this.map.setCenter(feature.geometry.bounds.getCenterLonLat());
								} else {
									this.map.zoomToExtent(feature.geometry.bounds, true);
								}
							}
						}, {
							tooltip : gettext('Export to drawings'),
							getClass: function(v, meta, rec) {
								var layer_name = this.get(0).activeTab.layer_name;
								return this.layersMetadata[layer_name].export_to_drawings? 'export-feature' : 'export-feature-disabled';
							},
							handler: function(grid, rowIndex, colIndex) {
								var layer_name = grid.layer_name;
								if (!this.layersMetadata[layer_name].export_to_drawings) {
									// do not allow export from this layer
									return;
								}
								grid.getSelectionModel().selectRow(rowIndex);
								var feature = grid.getStore().getAt(rowIndex).get('feature');

								var feature_pk = null;
								if (this.layersMetadata[layer_name]) {
									var feature_pks = [];
									Ext.each(this.layersMetadata[layer_name].pk_attributes, function(pk_attr_name) {
										 feature_pks.push(feature.attributes[pk_attr_name]);
									});
									feature_pk = feature_pks.join(',');
								}
								if (!feature_pk) {
									feature_pk = feature.fid.substring(feature.fid.lastIndexOf(".")+1);
								}
								feature.attributes.title = String.format('{0} - #{1}', layer_name, feature_pk);
								var description_format = gettext('Copy of feature #%(pk)s from layer %(layer)s');
								feature.attributes.description = interpolate(description_format, {pk: feature_pk, layer: layer_name}, true);
								var draw_action = Ext.getCmp('draw-action');
								draw_action.importFeatures([feature], true, true);
								draw_action.toggle(true);
								var draw_tab = 0;
								var geom_type = feature.geometry.CLASS_NAME.replace('Multi', '');
								if (geom_type === 'OpenLayers.Geometry.LineString') {
									draw_tab = 1;
								} else if (geom_type === 'OpenLayers.Geometry.Polygon') {
									draw_tab = 2;
								}
								draw_action.baseAction.window.drawPanel.setActiveTab(draw_tab);
							}
						}]
					});
				}

				Ext.each(this.layersMetadata[layer_name].attributes, function(layer_attrib) {
					var attr_name = layer_attrib.name;
					var attr_type = layer_attrib.type == 'INTEGER'? 'int' : layer_attrib.type == 'DOUBLE'? 'float' : 'string';
					if (attr_name == 'geometry' || attr_name == 'boundedBy') {return true;}
					fields.push({
						name: attr_name,
						type: attr_type
					});
					columns.push({
						id: attr_name,
						header: layer_attrib.alias? layer_attrib.alias : attr_name,
						dataIndex: attr_name,
						type: attr_type,
					});
				});

				var store = new GeoExt.data.FeatureStore({
					layer: flayer,
					fields: fields,
					features: layer_features,
					autoLoad: true
				});
				var grid_panel = new Ext.grid.GridPanel({
					title: layer_name,
					layer_name: layer_name,
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
							grid.getSelectionModel().selectControl.map.removeControl(grid.getSelectionModel().selectControl);
							grid.getSelectionModel().unbind();
						}
					}
				});
				this.featureinfo_tabpanel.add(grid_panel);
			}
			this.expand(false);
			this.featureinfo_tabpanel.setActiveTab(0);
			this.featureinfo_tabpanel.doLayout();
		} else {
			if (this.collapsed) {
				this.expand(false);
			}
		}
	},
	listeners: {
		collapse: function(panel) {
			this.setFeaturesLayersVisibility(false);
		},
		expand: function(panel) {
			this.setFeaturesLayersVisibility(true);
		}
	},
});

