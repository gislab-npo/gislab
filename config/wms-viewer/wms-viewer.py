#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
"""

import sys
from cgi import parse_qsl
from owslib.wms import WebMapService


DEBUG=True

def _get_resolutions(scales, units, resolution=96):
	"""Helper function to compute OpenLayers resolutions."""

	resolution = float(resolution)
	factor = {'in': 1.0, 'ft': 12.0, 'mi': 63360.0,
			'm': 39.3701, 'km': 39370.1, 'dd': 4374754.0}
	
	inches = 1.0 / resolution
	monitor_l = inches / factor[units]
	
	resolutions = []
	for m in scales:
		resolutions.append(monitor_l * int(m))
	return resolutions


def page(c):
	"""Return viewer application HTML code."""

	html = ''

	# head and javascript start
	html += """
	<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

        <link rel="stylesheet" type="text/css" href="static/ext-3.4.1/resources/css/ext-all.css"/>

        <script type="text/javascript" src="static/ext-3.4.1/adapter/ext/ext-base.js"></script>
        <script type="text/javascript" src="static/ext-3.4.1/ext-all.js"></script>

        <script type="text/javascript" src="static/OpenLayers-2.13/OpenLayers.js"></script>
        <script type="text/javascript" src="static/GeoExt-1.1/GeoExt.js"></script>

        <style type="text/css">
             .olControlNoSelect {background-color:rgba(200, 200, 200, 0.3)}
			 #dpiDetection {height: 1in; left: -100%%; position: absolute; top: -100%%; width: 1in;}
        </style>

        <title id="page-title">%(root_title)s</title>
        <script type="text/javascript">
		Ext.BLANK_IMAGE_URL = "static/images/s.gif";
	""" % c

	# configuration object
	html += """
		OpenLayers.DOTS_PER_INCH = %(resolution)s;
		var config = {
			projection: "%(projection)s",
			units: "%(units)s",
			resolutions: [%(resolutions)s],
			maxExtent: [%(extent)s],
		};

		var x = %(center_coord1)s;
		var y = %(center_coord2)s;
		var zoom = %(zoom)s;
		var layer = null;

	""" % c

	if DEBUG: html += """console.log("CONFIG: %s");""" % c

	# layer objects
	html += "var maplayers = ["
	for lay in c['layers']:
		html += """
		new OpenLayers.Layer.WMS(
		"%s",
		["%s&TRANSPARENT=TRUE"],
		{
			layers: "%s",
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
	),
	""" % (lay, c['ows_url'], lay, 'image/png')
	
	if c['blayers']:
		html += "new OpenLayers.Layer.OSM(),"

	html += "];"

	# GeoExt map GUI
	if c['blayers']:
		c['allOverlays'] = 'false'
	else:
		c['allOverlays'] = 'true'
	html += """
		var mappanel = new GeoExt.MapPanel({
			region: 'center',
			xtype: 'gx_mappanel',
			title: '%(root_title)s',
			zoom: 3,
			map: {
				allOverlays: %(allOverlays)s,
				units: config.units,
				projection: new OpenLayers.Projection(config.projection),
				resolutions: config.resolutions,
				maxExtent: new OpenLayers.Bounds(config.maxExtent[0], config.maxExtent[1],
					config.maxExtent[2], config.maxExtent[3]),
				controls: []
			},
			layers: maplayers
		});

		function main() {
			var layers_root = new Ext.tree.TreeNode({
				text: 'Layers',
				expanded: true,
				draggable: false
			});
	""" % c

	if c['blayers']:
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

	html += """
			layers_root.appendChild(new GeoExt.tree.OverlayLayerContainer({
				text: 'Overlays',
				map: mappanel.map,
				leaf: false,
				expanded: true,
				draggable: false,
				autoScroll: true,
			}));
			var layer_treepanel = new Ext.tree.TreePanel({
				region: 'center',
				title: 'Content',
				enableDD: true,
				root: layers_root,
				collapsible: false,
				border: false,
			});
		/*	var layer_legend = new GeoExt.LegendPanel({
				title: "Layer Legend",
				contentEl: 'layerlegend',
				border: false,
				region: 'south',
				height: 200,
				collapsible: true,
				split: true,
				autoScroll: true,
				ascending: false,
				map: mappanel.map,
				defaults: {cls: 'legend-item'}
			}); */
			var webgis = new Ext.Viewport({
				layout: "border",
				items: [
				/*	{
						region: 'north',
						contentEl: 'header',
						height: 54
					}, */
					mappanel,
					{
						region: 'west',
						xtype: 'panel',
						width: 200,
						split: true,
						border: false,
						layout: 'border',
						items: [layer_treepanel,]
					}
				]
			});
	""" % c

	# controls
	html += """
			mappanel.map.setCenter(new OpenLayers.LonLat(%(center_coord1)s, %(center_coord2)s), %(zoom)s);
			mappanel.map.addControl(new OpenLayers.Control.Scale());
			mappanel.map.addControl(new OpenLayers.Control.ScaleLine());
			mappanel.map.addControl(new OpenLayers.Control.MousePosition());
			mappanel.map.addControl(new OpenLayers.Control.PanZoomBar());
			mappanel.map.addControl(new OpenLayers.Control.Navigation());
			mappanel.map.addControl(new OpenLayers.Control.Attribution());
		};
	""" % c

	html += """
		Ext.QuickTips.init();
		Ext.onReady(main);
				</script>
			</head>
			<body>
				<div id="mappanel">Loading</div>
				<div id="layertree"></div>
				<div id="layerlegend"></div>
				<div id="overviewLegend" style="margin-left:10px"></div>
				<div id="dpiDetection"></div>
			</body>
		</html>
	"""

	return html


def application(environ, start_response):
	"""Return server response."""

	OWS_URL="http://192.168.50.5/cgi-bin/qgis_mapserv.fcgi" #  TODO: do not hardcode this
	DEFAULT_SCALES="1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500"
	PROJECTION_UNITS_DD=('EPSG:4326',)

	qs = dict(parse_qsl(environ['QUERY_STRING'])) # collect GET parameters
	qs = dict((k.upper(), v) for k, v in qs.iteritems()) # change GET parameters names to uppercase

	projectfile = '/storage/' + qs.get('PROJECT') # TODO: use Apache rewrite
	getcapabilities_url = "{0}/?map={1}&REQUEST=GetCapabilities".format(OWS_URL, projectfile)

	try:
		wms_service = WebMapService(getcapabilities_url, version="1.1.1") # read WMS GetCapabilities
	except:
		start_response('404 NOT FOUND', [('content-type', 'text/plain')])
		return ('Project file does not exist or it is not accessible.',)

	root_layer = None
	for layer in wms_service.contents.itervalues():
		if not layer.parent:
			root_layer = layer
			break
	if not root_layer: raise Exception("Root layer not found.")

	extent = root_layer.boundingBox[:-1]

	# set some parameters from GET request (can override parameters from WMS GetCapabilities)
	if qs.get('DPI'):
		resolution = qs.get('DPI')
	else:
		resolution = 96

	if qs.get('SCALES'):
		scales = map(int, qs.get('SCALES').split(","))
	else:
		scales = map(int, DEFAULT_SCALES.split(","))

	if qs.get('ZOOM'):
		zoom = qs.get('ZOOM')
	else:
		zoom = 0

	if qs.get('CENTER'):
		center_coord1 = qs.get('CENTER').split(',')[0]
		center_coord2 = qs.get('CENTER').split(',')[1]
	else:
		center_coord1 = (extent[0]+extent[2])/2.0
		center_coord2 = (extent[1]+extent[3])/2.0


	if qs.get('LAYERS'):
		layers_names = qs.get('LAYERS').split(',')
	else:
		layers_names = [layer.name.encode('UTF-8') for layer in root_layer.layers][::-1]

	c = {} # configuration dictionary which will be used in HTML template
	c['projectfile'] = projectfile
	c['projection'] = root_layer.boundingBox[-1]

	if c['projection'] in PROJECTION_UNITS_DD: # TODO: this is very naive
		c['units'] = 'dd'
	else:
		c['units'] = 'm'

	if qs.get('BLAYERS') in (None, 'true', 'TRUE') and c['projection'] == 'EPSG:3857':
		c['blayers'] = True
	else:
		c['blayers'] = False
	
	c['resolution'] = resolution
	c['extent'] = ",".join(map(str, extent))
	c['center_coord1'] = center_coord1
	c['center_coord2'] = center_coord2
	c['scales'] = scales
	c['zoom'] = zoom
	c['resolutions'] = ', '.join(str(r) for r in _get_resolutions(c['scales'], c['units'], c['resolution']))
#	c['author'] = wms_service.provider.contact.name.encode('UTF-8')
#	c['email'] = wms_service.provider.contact.email.encode('UTF-8')
#	c['organization'] = wms_service.provider.contact.organization.encode('UTF-8')

	c['root_layer'] = root_layer.name.encode('UTF-8')
	c['root_title'] = wms_service.identification.title.encode('UTF-8')
	c['layers'] = layers_names
	c['ows_url'] = '{0}/?map={1}&DPI={2}'.format(OWS_URL, projectfile, resolution)
	c['ows_get_capabilities_url'] = getcapabilities_url

	start_response('200 OK', [('Content-type','text/html')])
	return page(c)


# vim: set ts=4 sts=4 sw=4 noet:
