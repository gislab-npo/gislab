# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import os.path
import urllib2
import contextlib
import xml.etree.ElementTree as etree

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse

from webgis.viewer import forms
from webgis.viewer.qgis_wms import QgisGetProjectSettingsService

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

def getprint(request):
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
		ows_getprojectsettings_url = "{0}&SERVICE=WMS&REQUEST=GetProjectSettings".format(ows_url)
		getfeatureinfo_url = "{0}?map={1}&REQUEST=GetFeatureInfo".format(reverse('webgis.viewer.views.featureinfo'), projectfile)
		getprint_url = "{0}?map={1}&SERVICE=WMS&REQUEST=GetPrint".format(reverse('webgis.viewer.views.getprint'), projectfile)

		try:
			project_settings = QgisGetProjectSettingsService(ows_getprojectsettings_url)
		except Exception, e:
			return HttpResponse("Can't load project. Error: {0}".format(str(e)), content_type='text/plain', status=404);

		root_layer = project_settings.root_layer
		if not root_layer: raise Exception("Root layer not found.")

		layers = form.cleaned_data['layers']
		if layers:
			filtered_layers = []
			for layer_name in layers:
				for layer in project_settings.layers:
					if layer.name == layer_name:
						filtered_layers.append(layer)
			context['layers'] = filtered_layers
		else:
			context['layers'] = project_settings.layers

		visible_layers = form.cleaned_data["visible"]
		if visible_layers:
			context['visible_layers'] = visible_layers

		context.update({
			'project': project,
			'projectfile': projectfile,
			'ows_url': ows_url,
			'ows_getprojectsettings_url': ows_getprojectsettings_url,
			'getfeatureinfo_url': getfeatureinfo_url,
			'getprint_url': getprint_url,
			'project_extent': ",".join(map(str, root_layer.extent)),
			'projection': root_layer.projection,
			'featureinfo': 'application/vnd.ogc.gml' in project_settings.featureinfo_formats and projectfile,
			'print_composers': project_settings.print_composers,

			'root_title': project_settings.title,
			'author': project_settings.author,
			'email': project_settings.email,
			'organization': project_settings.organization,
			'abstract': project_settings.abstract
		})
	else:
		context.update({
			'project_extent': "-20037508.34,-20037508.34,20037508.34,20037508.34",
			'root_title': 'Empty Project'
		})

	context['osm'] = form.cleaned_data['osm'].upper() == "TRUE" or not project
	context['google'] = form.cleaned_data['google'].upper() or 'HYBRID' if not project else False
	osm_or_google = context['osm'] or context['google']
	if osm_or_google:
		context['projection'] = 'EPSG:3857'

	context['dpi'] = form.cleaned_data['dpi'] or 96

	scales = form.cleaned_data['scales'] or settings.WEBGIS_SCALES if not osm_or_google else None
	if scales:
		context['scales'] = scales

	context['zoom_extent'] = form.cleaned_data['extent'] or context['project_extent']
	context['units'] = 'dd' if context['projection'] in PROJECTION_UNITS_DD else 'm' # TODO: this is very naive
	if not osm_or_google:
		context['tile_resolutions'] = ', '.join(str(r) for r in _get_tile_resolutions(context['scales'], context['units'], context['dpi']))

	context['drawings'] = form.cleaned_data['drawings']

	if settings.DEBUG:
		context['debug'] = True
		context['config'] = dict(context)

	return render(request, "viewer/webgis.html", context, content_type="text/html")

