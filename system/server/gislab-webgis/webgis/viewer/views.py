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
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from webgis.viewer import forms
from webgis.viewer import models
from webgis.viewer.metadata_parser import MetadataParser


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


@login_required
def ows_request(request):
	url = "{0}?{1}".format(settings.WEBGIS_OWS_URL.rstrip("/"), request.environ['QUERY_STRING'])
	with contextlib.closing(urllib2.urlopen(url)) as resp:
		resp_content = resp.read()
		content_type = resp.info().getheader("Content-Type")
		status = resp.getcode()
		return HttpResponse(resp_content, content_type=content_type, status=status)

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

	context = {'dpi': 96}
	project = form.cleaned_data['project']

	scales = form.cleaned_data['scales'] or settings.WEBGIS_SCALES
	if scales:
		context['scales'] = scales

	if project:
		metadata_filename = os.path.join(settings.WEBGIS_PROJECT_ROOT, os.path.splitext(project)[0] + '.meta')
		try:
			metadata = MetadataParser(metadata_filename)
		except Exception, e:
			return HttpResponse("Can't load project. Error: {0}".format(str(e)), content_type='text/plain', status=404);

	# Authentication
	allow_anonymous = metadata.authentication['allow_anonymous'] if project else True
	require_superuser = metadata.authentication['require_superuser'] if project else False

	if not request.user.is_authenticated() and allow_anonymous:
		# login as quest and continue
		user = models.GislabUser.get_guest_user()
		if user:
			login(request, user)
		else:
			return HttpResponse("Anonymous user is not configured", content_type='text/plain', status=500)

	if (not allow_anonymous and (not request.user.is_authenticated() or request.user.is_guest)) or (require_superuser and not request.user.is_superuser):
		# redirect to login page
		login_url = reverse('login')
		return HttpResponseRedirect(set_query_parameters(login_url, {'next': request.build_absolute_uri()}))
	context['user'] = request.user


	if project:
		ows_url = '{0}?map={1}'.format(reverse('viewer:owsrequest'), project)
		ows_getprojectsettings_url = "{0}?map={1}&SERVICE=WMS&REQUEST=GetProjectSettings".format(settings.WEBGIS_OWS_URL, project)
		context['projection'] = metadata.projection
		context['units'] = {'meters': 'm', 'feet': 'ft', 'degrees': 'dd'}.get(metadata.units, 'dd')
	else:
		context['projection'] = 'EPSG:3857'
		context['units'] = 'dd'

	context['tile_resolutions'] = _get_tile_resolutions(context['scales'], context['units'], context['dpi'])

	if project:
		project_tile_resolutions = context['tile_resolutions']
		project_projection = context['projection']

		# converts tree with layers data into simple dictionary
		def collect_layers_capabilities(layer_data, capabilities=None):
			if capabilities is None:
				capabilities = {}
			sublayers = layer_data.get('layers')
			if sublayers:
				for sublayer_data in sublayers:
					collect_layers_capabilities(sublayer_data, capabilities)
			else:
				capabilities[layer_data['name']] = layer_data
			return capabilities

		# BASE LAYERS
		base_layers_capabilities = collect_layers_capabilities({'layers': metadata.base_layers}) if metadata.base_layers else {}
		base_layers_capabilities.update(SPECIAL_BASE_LAYERS)
		for layer_capabilities in base_layers_capabilities.itervalues():
			layer_type = layer_capabilities.get('type')
			if layer_type == 'WMSC':
				layer_resolutions = layer_capabilities['resolutions']
				layer_capabilities['min_resolution'] = layer_resolutions[-1]
				layer_capabilities['max_resolution'] = layer_resolutions[0]
				upper_resolutions = filter(lambda res: res > layer_capabilities['max_resolution'], project_tile_resolutions)
				lower_resolutions = filter(lambda res: res < layer_capabilities['min_resolution'], project_tile_resolutions)
				layer_capabilities['resolutions'] = upper_resolutions + layer_resolutions + lower_resolutions
			elif layer_type in ('WMS', 'BLANK'):
				layer_capabilities['resolutions'] = project_tile_resolutions
		base = form.cleaned_data['base']
		if base:
			try:
				skip_layers = None
				# ignore OSM and Google layers when project's projection is not EPSG:3857
				if context['projection'] != 'EPSG:3857':
					skip_layers = SPECIAL_BASE_LAYERS.keys()
					skip_layers.remove('BLANK')
				baselayers_tree = parse_layers_param(base, base_layers_capabilities, skip_layers=skip_layers)['layers']
			except LookupError, e:
				return HttpResponse("Unknown base layer: {0}".format(str(e)), content_type='text/plain', status=400);
		else:
			baselayers_tree = metadata.base_layers
		# ensure that a blank base layer is always used
		if not baselayers_tree:
			baselayers_tree = [base_layers_capabilities['BLANK']]
		context['base_layers'] = json.dumps(baselayers_tree)

		# OVERLAYS LAYERS
		layers = form.cleaned_data['overlay']
		# override layers tree with LAYERS GET parameter if provided
		if layers:
			overlays_capabilities = collect_layers_capabilities({'layers': metadata.overlays}) if metadata.overlays else {}
			try:
				layers_tree = parse_layers_param(layers, overlays_capabilities)['layers']
			except LookupError, e:
				return HttpResponse("Unknown overlayer: {0}".format(str(e)), content_type='text/plain', status=400);
		else:
			layers_tree = metadata.overlays
		context['layers'] = json.dumps(layers_tree) if layers_tree else None

		context.update({
			'project': project,
			'ows_url': ows_url,
			'wms_url': set_query_parameters(settings.WEBGIS_OWS_URL, {'map': project}),
			'ows_getprojectsettings_url': ows_getprojectsettings_url,
			'project_extent': metadata.extent,
			'print_composers': metadata.composer_templates,
			'root_title': metadata.title,
			'author': metadata.contact_person,
			'email': metadata.contact_mail,
			'organization': metadata.contact_organization,
			'abstract': metadata.abstract
		})
	else:
		context.update({
			'project_extent': [-20037508.34, -20037508.34, 20037508.34, 20037508.34],
			'root_title': 'Empty Project'
		})
		base = form.cleaned_data['base'] or '/OSM:1;GHYBRID:0'
		try:
			context['base_layers'] = json.dumps(parse_layers_param(base, SPECIAL_BASE_LAYERS)['layers'])
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

