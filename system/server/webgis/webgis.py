#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import os, sys
import webob
import urllib
from cgi import parse_qsl
from owslib.wms import WebMapService
from wsgiproxy.app import WSGIProxyApp

# otherwise handling proxy requests containing unicode characters fails
reload(sys)
sys.setdefaultencoding("utf-8")


def _get_tile_resolutions(scales, units, dpi=96):
	"""Helper function to compute OpenLayers tile resolutions."""

	dpi = float(dpi)
	factor = {'in': 1.0, 'ft': 12.0, 'mi': 63360.0,
			'm': 39.3701, 'km': 39370.1, 'dd': 4374754.0}
	
	inches = 1.0 / dpi
	monitor_l = inches / factor[units]
	
	resolutions = []
	for m in scales:
		resolutions.append(monitor_l * int(m))
	return resolutions


def page(c):
	"""Return WebGIS application HTML code."""

	html = ''

	# head and javascript start
	html += """
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

        <link rel="stylesheet" type="text/css" href="static/ext-3.4.1/resources/css/ext-all.css"/>
        <link rel="stylesheet" type="text/css" href="static/webgis/webgis.css"/>

        <script type="text/javascript" src="static/ext-3.4.1/adapter/ext/ext-base.js"></script>
        <script type="text/javascript" src="static/ext-3.4.1/ext-all.js"></script>

        <script type="text/javascript" src="static/OpenLayers-2.13/OpenLayers.js"></script>
        <script type="text/javascript" src="static/GeoExt-1.1/GeoExt.js"></script>
	""" % c

	if c['google']:
		html += """<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>"""

	html += """
        <title id="page-title">%(root_title)s</title>
    """ % c

	# configuration
	html += """
        <script type="text/javascript">
		function main() {

			Ext.BLANK_IMAGE_URL = "static/webgis/images/s.gif";
			OpenLayers.DOTS_PER_INCH = %(dpi)s;
			OpenLayers.ProxyHost = "/proxy/?url=";
			var config = {
				projection: "%(projection)s",
				units: "%(units)s",
				tile_resolutions: [%(tile_resolutions)s],
				maxExtent: [%(project_extent)s],
		};

		var x = %(center_coord1)s;
		var y = %(center_coord2)s;
		var zoom = %(zoom)s;
		var layer = null;
		var vector_data_balls = null;

	""" % c

	if c['debug']: html += """\tconsole.log("CONFIG: %s");\n""" % c

	# layers
	html += "\t\tvar maplayers = [];\n"

	# base layers
	if c['google']:
		html += """\t\tmaplayers.push(new OpenLayers.Layer.Google('Google %s',
							{type: google.maps.MapTypeId.%s,
							mapTypeId: '%s'}));\n
		""" % (c['google'].title(), c['google'], c['google'])

	if c['osm']: # seems that must be loaded after google layer
		html += "\t\tmaplayers.push(new OpenLayers.Layer.OSM());\n"

	# overlay layers
	html += """
		var overlays_group_layer = new OpenLayers.Layer.WMS(
			"OverlaysGroup",
			["%s&DPI=%s&TRANSPARENT=TRUE"],
			{
				layers: ["%s"],
				transparent: true,
				format: "%s",
			},
			{
				gutter: 0,
				isBaseLayer: false,
				buffer: 0,
				visibility: true,
				singleTile: true,
				// attribution: "",
			}
		);
	""" % (c['ows_url'], c['dpi'], '", "'.join(c['layers']), 'image/png')
	html += "\tmaplayers.push(overlays_group_layer);\n"

	# drawing layers
	html += """
		var vector_style = {
			styleMap: new OpenLayers.StyleMap({
				'default':{
					label: '${label}',
					fontSize: '12px',
					fontWeight: 'bold',
					labelAlign: 'lb',
					strokeColor: '#AA0000',
					strokeOpacity: 1,
					strokeWidth: 1.5,
					fillColor: '#FF0000',
					fillOpacity: 0.5,
					pointRadius: 6,
					labelYOffset: '6',
					labelXOffset: '6',
					fontColor: '#AA0000',
					labelOutlineColor: 'white',
					labelOutlineWidth: 2.5,
					labelOutlineOpacity: 0.5,
				},
				'select': {
					label: '${label}',
					fontSize: '12px',
					fontWeight: 'bold',
					labelAlign: 'lb',
					strokeColor: '#66CCCC',
					strokeOpacity: 1,
					strokeWidth: 1.5,
					fillColor: '#66CCCC',
					fillOpacity: 0.3,
					pointRadius: 6,
					labelYOffset: '6',
					labelXOffset: '6',
					fontColor: '#306060',
					labelOutlineColor: 'white',
					labelOutlineWidth: 2.5,
					labelOutlineOpacity: 0.5,
				},
				'modify': {
					label: '',
					fillColor: '#66CCCC',
					fillOpacity: 0.3,
					strokeColor: '#66CCCC',
					strokeOpacity: 1,
					strokeWidth: 2,
				}
			})
		};
		var points_layer = new OpenLayers.Layer.Vector('POINTS', vector_style);
		var lines_layer = new OpenLayers.Layer.Vector('LINES', vector_style);
		var polygons_layer = new OpenLayers.Layer.Vector('POLYGON', vector_style);
		maplayers.push(points_layer);
		maplayers.push(lines_layer);
		maplayers.push(polygons_layer);
	"""

	# map panel
	if c['osm'] or c['google']:
		c['allOverlays'] = 'false'
	else:
		c['allOverlays'] = 'true'

	html += """
		var mappanel = new GeoExt.MapPanel({
			region: 'center',
			title: '%(root_title)s',
			collapsible: false,
			zoom: 3,
			map: {
				allOverlays: %(allOverlays)s,
				units: config.units,
				projection: new OpenLayers.Projection(config.projection),
				resolutions: config.tile_resolutions,
				maxExtent: new OpenLayers.Bounds(config.maxExtent[0], config.maxExtent[1],
					config.maxExtent[2], config.maxExtent[3]),
				controls: []
			},
			layers: maplayers,
			items: [{
				xtype: "gx_zoomslider",
				aggressive: true,
				vertical: true,
				height: 150,
				x: 17,
				y: 85,
				plugins: new GeoExt.ZoomSliderTip()
			}],
			tbar: [],
			bbar: [],
			stateId: 'map',
		});
		var mappanel_container = mappanel;

		var ctrl, action;
	""" % c

	if c['has_featureinfo']:
		#featureinfo panel
		html += """
			var featureinfo_tabpanel = new Ext.TabPanel({
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
						Ext.each(mappanel.map.getLayersByName(new RegExp('^_featureinfolayer_.+')), function(layer) {
							layer.setVisibility(layer.name == tab_layer_name);
						});
					}
				}
			});

			var featureinfo_panel = new Ext.Panel({
				id: 'featureinfo-panel',
				title: 'Attributes',
				layout: 'fit',
				collapsible: true,
				collapsed: true,
				height: 120,
				split: true,
				region: 'south',
				animate: false,
				items: [featureinfo_tabpanel],

				clearFeaturesLayers: function() {
					featureinfo_tabpanel.removeAll(true);
					Ext.each(mappanel.map.getLayersByName(new RegExp('^_featureinfolayer_.+')), function(layer) {
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
							var flayer = mappanel.map.getLayer(features_layername);
							if (flayer == null) {
								flayer = new OpenLayers.Layer.Vector(features_layername, {
									eventListeners: {},
									styleMap: new OpenLayers.StyleMap({
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
									})
								});
								flayer.id = features_layername;
								flayer.displayInLayerSwitcher = false;
							}
							mappanel.map.addLayer(flayer);

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
								autoHeight: true,
								viewConfig: {
									forceFit:true,
								},
								cm: new Ext.grid.ColumnModel({
									defaults: {
										sortable: false
									},
									columns: columns
								}),
								sm: new GeoExt.grid.FeatureSelectionModel({
									autoPanMapOnSelection: true
								}),
								listeners: {
									'removed': function (grid, ownerCt ) {
										grid.selModel.unbind();
									}
								}
							});
							featureinfo_tabpanel.add(grid_panel);
						}
						this.expand(false);
						featureinfo_tabpanel.setActiveTab(0);
						featureinfo_tabpanel.doLayout();
					}
				},

				listeners: {
					collapse: function(panel) {
						this.clearFeaturesLayers();
					}
				},
			});
		"""
		html += """
			var mappanel_container = new Ext.Panel({
				layout: 'border',
				region: 'center',
				items: [
					mappanel,
					featureinfo_panel
				]
			});
		"""

		html+= """
		// Featureinfo Action
		ctrl = new OpenLayers.Control.WMSGetFeatureInfo({
			autoActivate: false,
			infoFormat: 'application/vnd.ogc.gml',
			maxFeatures: 10,
			queryVisible: true,
			eventListeners: {
				"getfeatureinfo": function(e) {
					featureinfo_panel.showFeatures(e.features);
				}
			}
		})
		action = new GeoExt.Action({
			control: ctrl,
			map: mappanel.map,
			cls: 'x-btn-icon',
			iconCls: 'featureinfo-icon',
			enableToggle: true,
			toggleGroup: 'tools',
			group: 'tools',
			tooltip: 'Feature info'
		})
		mappanel.getTopToolbar().add('-', action);
		""" % c

	html += """

		//Home Action
		action = new GeoExt.Action({
			handler: function() { mappanel.map.setCenter(new OpenLayers.LonLat(%(center_coord1)s, %(center_coord2)s), %(zoom)s); },
			map: mappanel.map,
			cls: 'x-btn-icon',
			iconCls: 'home-icon',
			tooltip: 'Home'
		});
		mappanel.getTopToolbar().add('-', action);

		//Pan Map Action
		action = new GeoExt.Action({
			control: new OpenLayers.Control.MousePosition({formatOutput: function(lonLat) {return '';}}),
			map: mappanel.map,
			toggleGroup: 'tools',
			group: 'tools',
			cls: 'x-btn-icon',
			iconCls: 'pan-icon',
			tooltip: 'Pan'
		});
		mappanel.getTopToolbar().add(action);

		//Zoom In Action
		action = new GeoExt.Action({
			control: new OpenLayers.Control.ZoomBox({alwaysZoom:true}),
			map: mappanel.map,
			toggleGroup: 'tools',
			group: 'tools',
			cls: 'x-btn-icon',
			iconCls: 'zoom-in-icon',
			tooltip: 'Zoom In'
		});
		mappanel.getTopToolbar().add(action);

		//Zoom Out Action
		action = new GeoExt.Action({
			control: new OpenLayers.Control.ZoomBox({alwaysZoom:true, out:true}),
			map: mappanel.map,
			toggleGroup: 'tools',
			group: 'tools',
			cls: 'x-btn-icon',
			iconCls: 'zoom-out-icon',
			tooltip: 'Zoom Out',
		});
		mappanel.getTopToolbar().add(action);

		// Navigation history - two 'button' controls
		ctrl = new OpenLayers.Control.NavigationHistory();
		mappanel.map.addControl(ctrl);

		action = new GeoExt.Action({
			control: ctrl.previous,
			disabled: true,
			cls: 'x-btn-icon',
			iconCls: 'previous-icon',
			tooltip: 'Previous in history',
		});
		mappanel.getTopToolbar().add(action);

		action = new GeoExt.Action({
			control: ctrl.next,
			disabled: true,
			cls: 'x-btn-icon',
			iconCls: 'next-icon',
			tooltip: 'Next in history',
		});
		mappanel.getTopToolbar().add(action, '-');

		var length = new OpenLayers.Control.Measure(OpenLayers.Handler.Path, {
			immediate: true,
			persist: true,
			geodesic: true, //only for projected projections
			eventListeners: {
				measurepartial: function(evt) {
					Ext.getCmp('measurement-info').setText('Length: ' + evt.measure.toFixed(2) + evt.units);
				},
				measure: function(evt) {
					Ext.getCmp('measurement-info').setText('Length: ' + evt.measure.toFixed(2) + evt.units);
				}
			}
		});

		var area = new OpenLayers.Control.Measure(OpenLayers.Handler.Polygon, {
			immediate: true,
			persist: true,
			geodesic: true, //only for projected projections
			eventListeners: {
				measurepartial: function(evt) {
					Ext.getCmp('measurement-info').setText('Area: ' + evt.measure.toFixed(2) + evt.units + '<sup>2</sup>');
				},
				measure: function(evt) {
					Ext.getCmp('measurement-info').setText('Area: ' + evt.measure.toFixed(2) + evt.units + '<sup>2</sup>');
				}
			}
		});

		mappanel.map.addControl(length);
		mappanel.map.addControl(area);

		var length_button = new Ext.Button({
			enableToggle: true,
			toggleGroup: 'tools',
			iconCls: 'length-measure-icon',
			toggleHandler: function(button, toggled) {
				if (toggled) {
					length.activate();
				} else {
					length.deactivate();
					Ext.getCmp('measurement-info').setText('');
				}
			},
			tooltip: 'Measure length'
		});

		var area_button = new Ext.Button({
			enableToggle: true,
			toggleGroup: 'tools',
			iconCls: 'area-measure-icon',
			toggleHandler: function(button, toggled) {
				if (toggled) {
					area.activate();
				} else {
					area.deactivate();
					Ext.getCmp('measurement-info').setText('');
				}
			},
			tooltip: 'Measure area'
		});
		mappanel.getTopToolbar().add(length_button, area_button);
	""" % c

	# Base class for drawing actions
	html += """
		DrawAction = Ext.extend(GeoExt.Action, {
			dialogTitle: '',
			constructor: function(config) {
				this.dialogTitle = config.dialogTitle;
				DrawAction.superclass.constructor.apply(this, arguments);
			},
			attributes_window: null,
			snap_control: null,
			modify_control: null,

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
					this.modify_control.setMap(this.control.map);
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
					targets: [points_layer, lines_layer, polygons_layer],
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
					this.enableSnapping();
					this.enableFeatureModify();
					this.showAttributesTable();
				} else {
					this.disableSnapping();
					if (this.modify_control) {
						this.modify_control.deactivate();
						this.modify_control.destroy();
					}
					if (this.control.layer.selectedFeatures.length > 0) {
						new OpenLayers.Control.SelectFeature(this.control.layer).unselectAll();
					}
					this.attribs_window.destroy();
					this.attribs_window = null;
				}
			},
		});
	"""
	# Draw points action
	html += """
		ctrl = new OpenLayers.Control.DrawFeature(
			points_layer,
			OpenLayers.Handler.Point,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						label: ''
					};
					// update feature on map
					points_layer.drawFeature(feature);
				}
			}
		);
		action = new DrawAction({
			control: ctrl,
			map: mappanel.map,
			dialogTitle: 'Points',
			cls: 'x-btn-icon',
			iconCls: 'draw-point-icon',
			enableToggle: true,
			toggleGroup: 'tools',
			tooltip: 'Draw points',
			scope: this,
			toggleHandler: function(action, toggled) {
				action.baseAction.toggleHandler(action, toggled);
			}
		});
		mappanel.getTopToolbar().add('-', action);
	"""
	# Draw lines action
	html += """
		ctrl = new OpenLayers.Control.DrawFeature(
			lines_layer,
			OpenLayers.Handler.Path,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						label: ''
					};
					// update feature on map
					lines_layer.drawFeature(feature);
				}
			}
		);
		action = new DrawAction({
			control: ctrl,
			map: mappanel.map,
			dialogTitle: 'Lines',
			cls: 'x-btn-icon',
			iconCls: 'draw-line-icon',
			enableToggle: true,
			toggleGroup: 'tools',
			tooltip: 'Draw lines',
			scope: this,
			toggleHandler: function(action, toggled) {
				action.baseAction.toggleHandler(action, toggled);
			}
		});
		mappanel.getTopToolbar().add(action);
	"""
	# Draw polygons action
	html += """
		ctrl = new OpenLayers.Control.DrawFeature(
			polygons_layer,
			OpenLayers.Handler.Polygon,
			{
				type: OpenLayers.Control.TYPE_TOOL,
				featureAdded: function(feature) {
					feature.attributes = {
						label: ''
					};
					// update feature on map
					polygons_layer.drawFeature(feature);
				}
			}
		);
		action = new DrawAction({
			control: ctrl,
			map: mappanel.map,
			dialogTitle: 'Polygons',
			cls: 'x-btn-icon',
			iconCls: 'draw-polygon-icon',
			enableToggle: true,
			toggleGroup: 'tools',
			tooltip: 'Draw polygons',
			scope: this,
			toggleHandler: function(action, toggled) {
				action.baseAction.toggleHandler(action, toggled);
			}
		});
		mappanel.getTopToolbar().add(action);
	"""

	# save ball
	html += """
		var action = new Ext.Action({
			cls: 'x-btn-icon',
			iconCls: 'save-icon',
			tooltip: 'Save drawing',
			handler: function() {
				var features_layers = [points_layer, lines_layer, polygons_layer];
				var features = [];
				Ext.each(features_layers, function(layer) {
					features = features.concat(layer.features);
				});
				if (features.length > 0) {
					var geojson = new OpenLayers.Format.GeoJSON().write(features, true);
					// add projection info
					if (mappanel.map.projection) {
						var geojson_obj = JSON.parse(geojson);
						geojson_obj.crs = new OpenLayers.Format.GeoJSON().createCRSObject(features[0]);
						geojson = JSON.stringify(geojson_obj, null, '    ');
					}
					Ext.Ajax.request({
						method: 'POST',
						url: '/proxy/?url=' + encodeURIComponent('http://balls.gis.lab/'),
						jsonData: geojson,
						headers: { 'Content-Type': 'application/geojson; charset=utf-8' },
						success: function(response) {
							vector_data_balls = response.responseText;
							fire_map_state_changed_event();
							Ext.get('geojson-link').dom.href = 'http://balls.gis.lab/?ID='+response.responseText;
							Ext.get('geojson-link').update(response.responseText);
							//window.location.assign('http://balls.gis.lab/?ID='+response.responseText);
						},
						failure: function(response, opts) {
							Ext.MessageBox.alert("Error", "Failed to save data.");
						}
					});
				} else {
					Ext.MessageBox.alert("Warning", "There is no data to be saved.");
				}
			}
		});
		var geojson_link = {
			id: 'geojson-link',
			xtype: 'box',
			autoEl: {tag: 'a', href: '#', html: ''}
		}
		mappanel.getTopToolbar().add('-', action, geojson_link);
	"""

	# tree node
	html += """
			var layers_root = new Ext.tree.TreeNode({
				text: 'Layers',
				expanded: true,
				draggable: false
			});
	"""

	# base layers tree
	if c['osm'] or c['google']:
		html += """
			layers_root.appendChild(new GeoExt.tree.BaseLayerContainer({
				text: 'Base Layers',
				map: mappanel.map,
				leaf: false,
				expanded: true,
				draggable: false,
				isTarget: false,
				split: true
			}));
		"""

	# overlay layers tree
	html += """
			layers_root.appendChild(new GeoExt.tree.LayerNode({
				text: 'Overlays',
				layer: overlays_group_layer,
				leaf: false,
				expanded: true,
				allowDrag: false,
				loader: {
					param: "LAYERS"
				}
			}));
	"""

	# layers tree
	html += """
			var layer_treepanel = new Ext.tree.TreePanel({
				title: 'Content',
				enableDD: false,
				root: layers_root,
				split: true,
				border: true,
				collapsible: false,
				cmargins: '0 0 0 0',
				autoScroll: true
			});
	"""

	# legend
	html += """
		var layer_legend = new GeoExt.LegendPanel({
			title: 'Legend',
			map: mappanel.map,
			border: false,
			ascending: false,
			autoScroll: true,
			filter: function(record) {
				var title = record.data.title;
				if (title == points_layer.name || title == lines_layer.name || title == polygons_layer.name) {
					return false;
				}
				return true;
			},
			defaults: {
				cls: 'legend-item',
				baseParams: {
					FORMAT: 'image/png',
					SYMBOLHEIGHT: '2',
					SYMBOLWIDTH: '4',
					LAYERFONTSIZE: '8',
					LAYERFONTBOLD: 'true',
					ITEMFONTSIZE: '8',
					ICONLABELSPACE: '15'
				}
			}
		});
	"""

	# properties
	html += """
			var properties = new Ext.Panel({
				title: 'Project',
				autoScroll: true,
				html: '<div class="x-panel-body-text"><p><b>Author: </b>%(author)s</p><p><b>E-mail: </b>%(email)s</p><p><b>Organization: </b>%(organization)s</p><b>Abstract: </b>%(abstract)s</p></div>'
			});
	""" % c

	# legend and properties accordion panel
	html += """
			var accordion = new Ext.Panel({
				layout: {
					type: 'accordion',
					titleCollapse: true,
					animate: false,
					activeOnTop: false
				},
				items: [
					layer_legend,
					properties
				]
			});
	"""

	# left panel
	html += """
			var left_panel = new Ext.Panel({
				region: 'west',
				width: 200,
				defaults: {
					width: '100%',
					flex: 1
				},
				layout: 'vbox',
				collapsible: true,
				layoutConfig: {
					align: 'stretch',
					pack: 'start'
				},
				items: [
					layer_treepanel,
					accordion
				]
			});
	"""

	# viewport
	html += """
			var webgis = new Ext.Viewport({
				layout: "border",
				items: [
					mappanel_container,
					left_panel
				]
			});
	"""

	# set visible layers if provided
	if 'visible_layers' in c:
		hidden_layers = [layer_name for layer_name in c['layers'] if layer_name not in c['visible_layers']]
		html += "\n"
		for hidden_layer in hidden_layers:
			html += "\t\t\tlayers_root.findChild('text', '%s', true).ui.toggleCheck(false);\n" % hidden_layer

	# controls
	html += """
			Ext.namespace("GeoExt.Toolbar");

			GeoExt.Toolbar.ControlDisplay = Ext.extend(Ext.Toolbar.TextItem, {

				control: null,
				map: null,

				onRender: function(ct, position) {
					this.text = this.text ? this.text : '&nbsp;';

					GeoExt.Toolbar.ControlDisplay.superclass.onRender.call(this, ct, position);
					this.control.div = this.el.dom;

					if (!this.control.map && this.map) {
						this.map.addControl(this.control);
					}
				}
			});
			var coords = new GeoExt.Toolbar.ControlDisplay({control: new OpenLayers.Control.MousePosition({separator: ' , '}), map: mappanel.map});

			mappanel.getBottomToolbar().add(new Ext.Toolbar.TextItem({text: config.projection}));
			mappanel.getBottomToolbar().add(' ', '-', '');
			mappanel.getBottomToolbar().add(coords);
			var measurement_output = new Ext.Toolbar.TextItem({
				id:'measurement-info',
				text: ''
			});
			mappanel.getBottomToolbar().add(' ', '-', ' ', measurement_output);

			mappanel.map.setCenter(new OpenLayers.LonLat(%(center_coord1)s, %(center_coord2)s), %(zoom)s);
			mappanel.map.addControl(new OpenLayers.Control.Scale());
			mappanel.map.addControl(new OpenLayers.Control.ScaleLine());
			mappanel.map.addControl(new OpenLayers.Control.PanPanel());
			mappanel.map.addControl(new OpenLayers.Control.ZoomPanel());
			mappanel.map.addControl(new OpenLayers.Control.Navigation());
			mappanel.map.addControl(new OpenLayers.Control.Attribution());
	""" % c

	# insert points from GET parameter
	if 'balls' in c:
		html += """
			vector_data_balls = '{0}';
		""".format(','.join(c['balls']))
		for ball in c['balls']:
			html += """
				Ext.Ajax.request({{
					method: 'GET',
					url: '/proxy/?url=' + encodeURIComponent('http://balls.gis.lab/?ID={0}'),
					success: function(response) {{
						var features = new OpenLayers.Format.GeoJSON().read(response.responseText);
						var points = [];
						var lines = [];
						var polygons = [];
						Ext.each(features, function(f) {{
							if (f.geometry.CLASS_NAME == 'OpenLayers.Geometry.Point')
								points.push(f);
							if (f.geometry.CLASS_NAME == 'OpenLayers.Geometry.LineString')
								lines.push(f);
							if (f.geometry.CLASS_NAME == 'OpenLayers.Geometry.Polygon')
								polygons.push(f);
						}});
						points_layer.addFeatures(points);
						lines_layer.addFeatures(lines);
						polygons_layer.addFeatures(polygons);
					}},
					failure: function(response, opts) {{
						Ext.MessageBox.alert("Error", "Failed to fetch vector data (ball: {0})");
					}}
				}});
			""".format(ball)

	# permalink
	html += """
		// create permalink provider
		var permalink_provider = new GeoExt.state.PermalinkProvider({encodeType: false});

		// set it in the state manager
		Ext.state.Manager.setProvider(permalink_provider);

		var permalink = new Ext.Toolbar.TextItem({text: '<a target="_blank" href="#">Permalink</a>'});
		mappanel.getBottomToolbar().add('->', permalink);

		// Register listeners for custom map state changes and generate events for permalink update
		var fire_map_state_changed_event = function(obj) {
			permalink_provider.fireEvent('statechange', permalink_provider, "map", {});
		};
		var overlays_node = layers_root.findChild('text', 'Overlays');
		overlays_node.eachChild(function(node) {
			node.on({
				checkchange: fire_map_state_changed_event
			});
		});

		permalink_provider.on({
			statechange: function(provider, name, value) {
				var map = mappanel.map;
				var all_layers = [];
				var visible_layers = [];
				overlays_node.eachChild(function(node) {
					all_layers.push(node.attributes.text);
					if (node.attributes.checked) {
						visible_layers.push(node.attributes.text);
					}
				});
				var parameters = {
					PROJECT: '%(project)s',
					DPI: '%(dpi)s',
					SCALES: '%(scales)s',
					ZOOM: map.getZoom(),
					CENTER: map.getCenter().toShortString(), //.replace(' ', ''),
					LAYERS: all_layers.join(',')
				};
				var osm_layer = map.getLayersByClass('OpenLayers.Layer.OSM')[0];
				if (osm_layer) {
					parameters.OSM = 'true';
				}
				var google_layer = map.getLayersByClass('OpenLayers.Layer.Google')[0];
				if (google_layer) {
					parameters.GOOGLE = google_layer.mapTypeId;
				}
				if (visible_layers.length < overlays_node.childNodes.length) {
					parameters.VISIBLE = visible_layers.join(',');
				}
				if (vector_data_balls) {
					parameters.BALLS = vector_data_balls;
				}
				var link = [location.protocol, '//', location.host, location.pathname, '?'].join('');
				var qs = [];
				for (var param_name in parameters) {
					qs.push(encodeURIComponent(param_name) + "=" + encodeURIComponent(parameters[param_name]));
				}
				link += qs.join("&");
				permalink.setText('<a target="_blank" href="' + link + '">Permalink</a>');
			}
		});
	""" % c

	html += """
		}; // end of main function
	"""
	html += """
		Ext.QuickTips.init();
		Ext.onReady(main);
				</script>
			</head>
			<body>
				<div id="overviewLegend" style="margin-left:10px"></div>
				<div id="dpiDetection"></div>
			</body>
		</html>
	"""

	return html


def application(environ, start_response):
	"""Return server response."""

	if environ["PATH_INFO"].startswith("/proxy/"):
		url = None
		#extra_query_params = []
		for name, value in parse_qsl(environ['QUERY_STRING']):
			if name.lower() == "url":
				url = urllib.unquote(value)
				break
		#	else:
		#		extra_query_params.append((name, value))
		if url is None:
			raise Exception("Invalid proxy request: missing URL parameter")
		req = webob.Request.blank(url)
		environ['QUERY_STRING'] = req.query_string #urllib.urlencode(extra_query_params)
		environ['PATH_INFO'] = req.path_info
		host_url = req.host_url
		proxy_req = webob.request.Request(environ)
		resp = proxy_req.get_response(WSGIProxyApp(host_url))
		return resp(environ, start_response)

	PROJECTION_UNITS_DD=('EPSG:4326',)

	qs = dict(parse_qsl(environ['QUERY_STRING'])) # collect GET parameters
	qs = dict((k.upper(), v) for k, v in qs.iteritems()) # change GET parameters names to uppercase

	c = {} # configuration

	c['debug'] = False
	if 'WEBGIS_DEBUG' in environ:
		if environ['WEBGIS_DEBUG'].upper() == 'TRUE': c['debug'] = True

	try:
		c['project'] = qs.get('PROJECT')
		c['projectfile'] = os.path.join(environ['WEBGIS_PROJECT_ROOT'], c['project'])
		c['ows_url'] = '{0}/?map={1}'.format(environ['WEBGIS_OWS_URL'], c['projectfile'])
		c['ows_getcapabilities_url'] = "{0}&REQUEST=GetCapabilities".format(c['ows_url'])

		wms_service = WebMapService(c['ows_getcapabilities_url'], version="1.1.1") # read WMS GetCapabilities
	except Exception, e:
		start_response('404 NOT FOUND', [('content-type', 'text/plain')])
		return ("Can't load project. Error: {0}".format(str(e)),)

	root_layer = None
	for layer in wms_service.contents.itervalues():
		if not layer.parent:
			root_layer = layer
			break
	if not root_layer: raise Exception("Root layer not found.")


	c['osm'] = False
	if qs.get('OSM'):
		if qs.get('OSM').upper() == 'TRUE': c['osm'] = True

	if qs.get('GOOGLE'):
		c['google'] = qs.get('GOOGLE').upper()
	else:
		c['google'] = False

	if qs.get('LAYERS'):
		layers_names = qs.get('LAYERS').split(',')
		layers_names.reverse()
		c['layers'] = layers_names
	else:
		c['layers'] = [layer.name.encode('UTF-8') for layer in root_layer.layers][::-1]

	if qs.get('VISIBLE'):
		c['visible_layers'] = [layer_name.strip() for layer_name in qs.get('VISIBLE').split(",")]

	if c['osm'] or c['google']:
		c['projection'] = 'EPSG:3857'
	else:
		c['projection'] = root_layer.boundingBox[-1]

	project_extent = root_layer.boundingBox[:-1]
	c['project_extent'] = ",".join(map(str, project_extent))

	if qs.get('DPI'):
		c['dpi'] = qs.get('DPI')
	else:
		c['dpi'] = 96

	if qs.get('SCALES'):
		c['scales'] = qs.get('SCALES')
	else:
		c['scales'] = environ['WEBGIS_SCALES']

	if qs.get('ZOOM'):
		c['zoom'] = qs.get('ZOOM')
	else:
		c['zoom'] = 0

	if qs.get('CENTER'):
		c['center_coord1'] = qs.get('CENTER').split(',')[0]
		c['center_coord2'] = qs.get('CENTER').split(',')[1]
	else:
		c['center_coord1'] = (project_extent[0]+project_extent[2])/2.0
		c['center_coord2'] = (project_extent[1]+project_extent[3])/2.0

	if c['projection'] in PROJECTION_UNITS_DD: # TODO: this is very naive
		c['units'] = 'dd'
	else:
		c['units'] = 'm'

	if qs.get('BALLS'):
		points_data = qs.get('BALLS')
		c['balls'] = qs.get('BALLS').split(',')

	c['tile_resolutions'] = ', '.join(str(r) for r in _get_tile_resolutions(map(int, c['scales'].split(",")), c['units'], c['dpi']))
	c['root_title'] = wms_service.identification.title.encode('UTF-8')
	c['author'] = wms_service.provider.contact.name.encode('UTF-8') if wms_service.provider.contact.name else ''
	c['email'] = wms_service.provider.contact.email.encode('UTF-8') if wms_service.provider.contact.email else ''
	c['organization'] = wms_service.provider.contact.organization.encode('UTF-8') if wms_service.provider.contact.organization else ''
	c['abstract'] = wms_service.identification.abstract.encode('UTF-8') if wms_service.identification.abstract else ''

	has_featureinfo = False
	for operation in wms_service.operations:
		if operation.name == 'GetFeatureInfo':
			has_featureinfo = 'application/vnd.ogc.gml' in operation.formatOptions
			break
	c['has_featureinfo'] = has_featureinfo

	start_response('200 OK', [('Content-type','text/html')])
	return page(c)


# vim: set ts=4 sts=4 sw=4 noet:
