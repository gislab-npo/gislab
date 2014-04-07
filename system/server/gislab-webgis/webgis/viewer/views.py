# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import json
import os.path
import urllib2
import contextlib
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
import xml.etree.ElementTree as etree

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse

from webgis.viewer import forms
from webgis.viewer.wms import WmsGetCapabilitiesService
from webgis.viewer.qgis_wms import QgisGetProjectSettingsService

PROJECTION_UNITS_DD=('EPSG:4326',)
SPECIAL_BASE_LAYERS = {
	'BLANK': {'name': 'BLANK', 'type': 'BLANK', 'title': 'Blank Layer'},
	'OSM': {'name': 'OSM', 'type': 'OSM', 'title': 'Open Street Map'},
	'GHYBRID': {'name': 'GHYBRID', 'type': 'google', 'title': 'Google Hybrid'},
	'GROADMAP': {'name': 'GROADMAP', 'type': 'google', 'title': 'Google Roadmap'},
	'GSATELLITE': {'name': 'GSATELLITE', 'type': 'google', 'title': 'Google Satellite'},
	'GTERRAIN': {'name': 'GTERRAIN', 'type': 'google', 'title': 'Google Terrain'},
}

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

def set_query_parameters(url, params_dict):
	"""Given a URL, set or replace a query parameters and return the
	modified URL. Parameters are case insensitive.

	>>> set_query_parameters('http://example.com?foo=bar&biz=baz', {'foo': 'stuff'})
	'http://example.com?foo=stuff&biz=baz'

	"""
	url_parts = list(urlsplit(url))
	query_params = parse_qs(url_parts[3])

	params = dict(params_dict)
	new_params_names = [name.lower() for name in params_dict.iterkeys()]
	for name, value in query_params.iteritems():
		if name.lower() not in new_params_names:
			params[name] = value

	url_parts[3] = urlencode(params, doseq=True)
	return urlunsplit(url_parts)


def getfeatureinfo(request):
	url = "{0}?{1}".format(settings.WEBGIS_OWS_URL.rstrip("/"), request.environ['QUERY_STRING'])
	resp = urllib2.urlopen(url)
	resp_content = resp.read()
	content_type = resp.info().getheader("Content-Type")
	resp.close()
	return HttpResponse(resp_content, content_type=content_type)

def getprint(request):
	url = "{0}?{1}".format(settings.WEBGIS_OWS_URL.rstrip("/"), request.environ['QUERY_STRING'])
	resp = urllib2.urlopen(url)
	resp_content = resp.read()
	content_type = resp.info().getheader("Content-Type")
	resp.close()
	return HttpResponse(resp_content, content_type=content_type)


def parse_layers_param(layers_string, layers_capabilities, skip_layers=None):
	tree = {
		'name': '',
		'layers': []
	}
	parts = layers_string.replace(';/', ';//').split(';/')
	for subtree_string in parts:
		location = os.path.dirname(subtree_string)
		parent = tree
		if location != '/':
			for parent_name in location.split('/')[1:]:
				#if 'layers' not in parent:
				#	parent['layers'] = []
				parent_exists = False
				for child in parent['layers']:
					if child['name'] == parent_name:
						parent = child
						parent_exists = True
						break
				if not parent_exists:
					new_parent = {
						'name': parent_name,
						'layers': []
					}
					parent['layers'].append(new_parent)
					parent = new_parent
		layers_string = os.path.basename(subtree_string)
		for layer_string in layers_string.split(';'):
			layer_info = layer_string.split(':')
			layer_name = layer_info[0]
			if skip_layers and layer_name in skip_layers:
				continue
			layer = layers_capabilities.get(layer_name)
			if layer is None:
				raise LookupError(layer_name)

			if len(layer_info) > 1:
				layer['visible'] = int(layer_info[1]) == 1
			if len(layer_info) > 2:
				layer['opacity'] = float(layer_info[2])
			parent['layers'].append(layer)
	return tree

def page(request):
	# make GET parameters not case sensitive
	params = dict((k.lower(), v) for k, v in request.GET.iteritems()) # change GET parameters names to uppercase
	form = forms.ViewerForm(params)
	if not form.is_valid():
		raise Http404

	context = {}
	context['dpi'] = 96
	project = form.cleaned_data['project']

	scales = form.cleaned_data['scales'] or settings.WEBGIS_SCALES
	if scales:
		context['scales'] = scales

	context['projection'] = 'EPSG:3857'

	if project:
		ows_url = '{0}?map={1}'.format(settings.WEBGIS_OWS_URL, project)
		ows_getprojectsettings_url = "{0}&SERVICE=WMS&REQUEST=GetProjectSettings".format(ows_url)
		getfeatureinfo_url = "{0}?map={1}&REQUEST=GetFeatureInfo".format(reverse('webgis.viewer.views.getfeatureinfo'), project)
		getprint_url = "{0}?map={1}&SERVICE=WMS&REQUEST=GetPrint".format(reverse('webgis.viewer.views.getprint'), project)

		try:
			project_settings = QgisGetProjectSettingsService(ows_getprojectsettings_url)
		except Exception, e:
			return HttpResponse("Can't load project. Error: {0}".format(str(e)), content_type='text/plain', status=404);

		root_layer = project_settings.root_layer
		if not root_layer: raise Exception("Root layer not found.")

		context['projection'] = root_layer.projection

	context['units'] = 'dd' if context['projection'] in PROJECTION_UNITS_DD else 'm' # TODO: this is very naive
	context['tile_resolutions'] = _get_tile_resolutions(context['scales'], context['units'], context['dpi'])

	if project:
		baselayers_capabilities = {}
		overlays_capabilities = {}
		def process_layer_info(layer_info):
			if layer_info.sublayers:
				baselayer_nodes = []
				overlay_nodes = []
				for sublayer_info in layer_info.sublayers:
					baselayer_node, overlay_node = process_layer_info(sublayer_info)
					if baselayer_node:
						baselayer_nodes.append(baselayer_node)
					if overlay_node:
						overlay_nodes.append(overlay_node)
				baselayer_node = {
					'name': layer_info.name,
					'layers': baselayer_nodes
				} if baselayer_nodes else None
				overlay_node = {
					'name': layer_info.name,
					'layers': overlay_nodes
				} if overlay_nodes else None
				return baselayer_node, overlay_node
			else:
				if layer_info.properties['providerType'] == 'wms':
					base_layer_data = {
						'name': layer_info.name,
						'visible': layer_info.properties.get('visible') == '1',
						'url': layer_info.properties['url'],
						'image_format': layer_info.properties['imageFormat'],
						'extent': layer_info.extent,
						'dpi': context['dpi']
					}
					baselayers_capabilities[layer_info.name] = base_layer_data
					return base_layer_data, None
				else:
					layer_data = {
						'name': layer_info.name,
						'visible': layer_info.properties.get('visible') == '1',
						'queryable': layer_info.properties.get('queryable') == '1',
						'geom_type': layer_info.properties.get('geomType'),
						'attributes': layer_info.attributes,
						'attribution': layer_info.attribution
					}
					overlays_capabilities[layer_info.name] = layer_data
					return None, layer_data

		baselayers_tree, layers_tree = process_layer_info(project_settings.root_layer)
		layers = form.cleaned_data['overlay']
		# override layers tree with LAYERS GET parameter if provided
		if layers:
			try:
				layers_tree = parse_layers_param(layers, overlays_capabilities)
			except LookupError, e:
				return HttpResponse("Unknown overlayer: {0}".format(str(e)), content_type='text/plain', status=400);

		SPECIAL_BASE_LAYERS['BLANK']['resolutions'] = context['tile_resolutions']
		baselayers_capabilities.update(SPECIAL_BASE_LAYERS)
		base = form.cleaned_data['base']
		if base:
			try:
				skip_layers = None
				# ignore OSM and Google layers when project's projection is not EPSG:3857
				if context['projection'] != 'EPSG:3857':
					skip_layers = SPECIAL_BASE_LAYERS.keys()
					skip_layers.remove('BLANK')
				baselayers_tree = parse_layers_param(base, baselayers_capabilities, skip_layers=skip_layers)
			except LookupError, e:
				return HttpResponse("Unknown base layer: {0}".format(str(e)), content_type='text/plain', status=400);

		# ensure that a blank base layer is always used
		if not baselayers_tree:
			baselayers_tree = {'name': '', 'layers': [baselayers_capabilities['BLANK']]}

		project_tile_resolutions = context['tile_resolutions']
		project_projection = context['projection']
		base_layers_capabilities = {}
		unavailable_wms_servers = []
		# Fill additional properties of WMS layers from GetCapabilities response
		for baselayer_name, base_layer in baselayers_capabilities.iteritems():
			if baselayer_name in SPECIAL_BASE_LAYERS:
				continue
			wms_server_url = base_layer['url']
			if wms_server_url not in base_layers_capabilities and wms_server_url not in unavailable_wms_servers:
				try:
					get_capabilities_url = set_query_parameters(wms_server_url, {'SERVICE': 'WMS', 'REQUEST': 'GetCapabilities'})
					capabilities = WmsGetCapabilitiesService(get_capabilities_url)
					base_layers_capabilities[wms_server_url] = capabilities
				except Exception, e:
					unavailable_wms_servers.append(wms_server_url)
			capabilities = base_layers_capabilities.get(wms_server_url)
			if capabilities:
				if baselayer_name in capabilities.wmsc_layers:
					wmsc_layer = capabilities.wmsc_layers[baselayer_name]
					base_layer['type'] = 'WMSC'
					base_layer['resolutions'] = wmsc_layer.resolutions
					base_layer['extent'] = wmsc_layer.extent
					upper_resolutions = filter(lambda res: res > wmsc_layer.resolutions[0], project_tile_resolutions)
					lower_resolutions = filter(lambda res: res < wmsc_layer.resolutions[-1], project_tile_resolutions)
					base_layer['resolutions'] = upper_resolutions + wmsc_layer.resolutions + lower_resolutions
					base_layer['min_resolution'] = wmsc_layer.resolutions[-1]
					base_layer['max_resolution'] = wmsc_layer.resolutions[0]
				elif baselayer_name in capabilities.wms_layers:
					wms_layer = capabilities.wms_layers[baselayer_name]
					if project_projection in wms_layer.projections:
						base_layer['type'] = 'WMS'
						base_layer['resolutions'] = project_tile_resolutions
						layer = wms_layer
						while project_projection not in layer.extents and layer.parent:
							layer = layer.parent
						base_layer['extent'] = layer.extents.get(project_projection)
					else:
						base_layer['type'] = 'UNAVAILABLE'
				else:
					base_layer['type'] = 'UNAVAILABLE'
			else:
				base_layer['type'] = 'UNAVAILABLE'

		context['base_layers'] = json.dumps(baselayers_tree.values()[0]) if baselayers_tree else None
		context['layers'] = json.dumps(layers_tree.values()[0]) if layers_tree else None

		context.update({
			'project': project,
			'ows_url': ows_url,
			'ows_getprojectsettings_url': ows_getprojectsettings_url,
			'getfeatureinfo_url': getfeatureinfo_url,
			'getprint_url': getprint_url,
			'project_extent': root_layer.extent,
			'featureinfo': 'application/vnd.ogc.gml' in project_settings.featureinfo_formats and project,
			'print_composers': project_settings.print_composers,

			'root_title': project_settings.title,
			'author': project_settings.author,
			'email': project_settings.email,
			'organization': project_settings.organization,
			'abstract': project_settings.abstract
		})
	else:
		context.update({
			'project_extent': [-20037508.34, -20037508.34, 20037508.34, 20037508.34],
			'root_title': 'Empty Project'
		})
		base = form.cleaned_data['base'] or '/OSM:1;GHYBRID:0'
		try:
			context['base_layers'] = json.dumps(parse_layers_param(base, SPECIAL_BASE_LAYERS).values()[0])
		except LookupError, e:
			return HttpResponse("Unknown base layer: {0}".format(str(e)), content_type='text/plain', status=400);

	google = False
	if context.get('base_layers'):
		for name, baselayer_info in SPECIAL_BASE_LAYERS.iteritems():
			if baselayer_info.get('type') == 'google' and name in context['base_layers']:
				google = True
				break
	context['google'] = google
	context['zoom_extent'] = form.cleaned_data['extent'] or context['project_extent']
	context['drawings'] = form.cleaned_data['drawings']

	if settings.DEBUG:
		context['debug'] = True
		context['config'] = dict(context)

	return render(request, "viewer/webgis.html", context, content_type="text/html")

