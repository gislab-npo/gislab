# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import os.path
import urllib2

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from owslib.wms import WebMapService

from webgis.viewer import forms


PROJECTION_UNITS_DD=('EPSG:4326',)

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


def featureinfo(request):
	url = "{0}/?{1}".format(settings.WEBGIS_OWS_URL.rstrip("/"), request.environ['QUERY_STRING'])
	resp = urllib2.urlopen(url)
	resp_content = resp.read()
	content_type = resp.info().getheader("Content-Type")
	resp.close()
	return HttpResponse(resp_content, content_type=content_type)

def page(request):
	# make GET parameters not case sensitive
	params = dict((k.lower(), v) for k, v in request.GET.iteritems()) # change GET parameters names to uppercase
	form = forms.ViewerForm(params)
	if not form.is_valid():
		raise Http404

	context = {}
	project = form.cleaned_data['project']
	if project:
		projectfile = os.path.join(settings.WEBGIS_PROJECT_ROOT, project)
		ows_url = '{0}/?map={1}'.format(settings.WEBGIS_OWS_URL, projectfile)
		ows_getcapabilities_url = "{0}&REQUEST=GetCapabilities".format(ows_url)
		getfeatureinfo_url = "{0}?map={1}&REQUEST=GetFeatureInfo".format(reverse('webgis.viewer.views.featureinfo'), projectfile)
		try:
			wms_service = WebMapService(ows_getcapabilities_url, version="1.1.1") # read WMS GetCapabilities
		except Exception, e:
			return HttpResponse("Can't load project. Error: {0}".format(str(e)), content_type='text/plain', status=404);

		root_layer = None
		for layer in wms_service.contents.itervalues():
			if not layer.parent:
				root_layer = layer
				break
		if not root_layer: raise Exception("Root layer not found.")

		featureinfo = False
		for operation in wms_service.operations:
			if operation.name == 'GetFeatureInfo':
				featureinfo = 'application/vnd.ogc.gml' in operation.formatOptions
				break
		context.update({
			'project': project,
			'projectfile': projectfile,
			'ows_url': ows_url,
			'ows_getcapabilities_url': ows_getcapabilities_url,
			'getfeatureinfo_url': getfeatureinfo_url,
			'project_extent': ",".join(map(str, root_layer.boundingBox[:-1])),
			'projection': root_layer.boundingBox[-1],
			'featureinfo': featureinfo,

			'root_title': wms_service.identification.title.encode('UTF-8'),
			'author': wms_service.provider.contact.name.encode('UTF-8') if wms_service.provider.contact.name else '',
			'email': wms_service.provider.contact.email.encode('UTF-8') if wms_service.provider.contact.email else '',
			'organization': wms_service.provider.contact.organization.encode('UTF-8') if wms_service.provider.contact.organization else '',
			'abstract': wms_service.identification.abstract.encode('UTF-8') if wms_service.identification.abstract else ''
		})
	else:
		context.update({
			'project_extent': "-20037508.34,-20037508.34,20037508.34,20037508.34",
			'root_title': 'Empty Project'
		})

	context['osm'] = form.cleaned_data['osm'].upper() == "TRUE" or not project
	context['google'] = form.cleaned_data.get('google', 'hybrid' if not project else '').upper() or False
	osm_or_google = context['osm'] or context['google']
	if osm_or_google:
		context['projection'] = 'EPSG:3857'


	layers = form.cleaned_data['layers']
	layers.reverse()
	if not layers and project:
		layers = [layer.name.encode('UTF-8') for layer in root_layer.layers][::-1]
	if layers:
		context['layers'] = layers
		visile_layers = form.cleaned_data["visible"]
		if visile_layers:
			context['visible_layers'] = visile_layers

	context['dpi'] = form.cleaned_data['dpi'] or 96

	scales = form.cleaned_data['scales'] or settings.WEBGIS_SCALES if not osm_or_google else None
	if scales:
		context['scales'] = scales

	context['zoom_extent'] = form.cleaned_data['extent'] or context['project_extent']
	context['units'] = 'dd' if context['projection'] in PROJECTION_UNITS_DD else 'm' # TODO: this is very naive
	if not osm_or_google:
		context['tile_resolutions'] = ', '.join(str(r) for r in _get_tile_resolutions(context['scales'], context['units'], context['dpi']))

	context['balls'] = form.cleaned_data['balls']

	if settings.DEBUG:
		context['debug'] = True
		context['config'] = dict(context)

	return render(request, "viewer/webgis.html", context, content_type="text/html")

