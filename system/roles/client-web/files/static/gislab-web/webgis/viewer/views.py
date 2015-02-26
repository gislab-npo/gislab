# -*- coding: utf-8 -*-

import re
import json
import os.path
import hashlib

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from webgis.viewer import forms
from webgis.viewer import models
from webgis.viewer.client import WebgisClient, LoginRequired
from webgis.viewer.metadata_parser import MetadataParser
from webgis.libs.auth.decorators import basic_authentication
from webgis.libs.utils import secure_url, set_query_parameters


class WebClient(WebgisClient):

	def get_ows_url(self, request):
		return set_query_parameters(reverse('viewer:owsrequest'), {'MAP': self.ows_project+'.qgs'})

	def get_mapcache_tile_url(self, request):
		project_hash = hashlib.md5(self.project).hexdigest()
		mapcache_url = reverse('viewer:tile', kwargs={'project_hash': project_hash, 'publish': self.project_metadata.publish_date_unix, 'layers_hash': '__layers__', 'x': 0, 'y': 0, 'z': 0, 'format': 'png'})
		return mapcache_url.split('/__layers__/')[0]+'/'

	def get_mapcache_legend_url(self, request):
		project_hash = hashlib.md5(self.project).hexdigest()
		legend_url = reverse('viewer:legend', kwargs={'project_hash': project_hash, 'publish': self.project_metadata.publish_date_unix, 'layer_hash': '__layer__', 'zoom': 0, 'format': 'png'})
		return legend_url.split('/__layer__/')[0]+'/'

	def get_vectorlayers_url(self, request):
		return set_query_parameters(reverse('viewer:vectorlayers'), {'PROJECT': self.ows_project})


	def render(self, request, project_data):
		project_data['dpi'] = 96
		project_data['user'] = request.user
		project_data['base_layers'] = json.dumps(project_data['base_layers'])
		project_data['layers'] = json.dumps(project_data['layers']) if 'layers' in project_data else '[]'
		project_data['topics'] = json.dumps(project_data['topics']) if 'topics' in project_data else '[]'
		if settings.DEBUG:
			project_data['debug'] = True
			project_data['config'] = dict(project_data)
		return render(request, "viewer/webgis.html", project_data, content_type="text/html")

client = WebClient()

def page(request):
	try:
		return client.project_request(request)
	except LoginRequired, e:
		# redirect to login page
		login_url = secure_url(request, reverse('login'))
		return HttpResponseRedirect(set_query_parameters(login_url, {'next': secure_url(request)}))

@basic_authentication(realm="OWS API")
def ows_request(request):
	return client.ows_request(request)

@login_required
def tile(request, project_hash, publish, layers_hash=None, z=None, x=None, y=None, format=None):
	return client.mapcache_tile_request(request, project_hash, publish, layers_hash=layers_hash, z=z, x=x, y=y, format=format)

@login_required
def legend(request, project_hash, publish, layer_hash=None, zoom=None, format=None):
	return client.mapcache_legend_request(request, project_hash, publish, layer_hash=layer_hash, zoom=zoom, format=format)

@login_required
def vector_layers(request):
	return client.vector_layers_request(request)


def user_projects(request, username):
	if not request.user.is_authenticated() or request.user.is_guest:
		# redirect to login page
		login_url = secure_url(request, reverse('login'))
		return HttpResponseRedirect(set_query_parameters(login_url, {'next': secure_url(request)}))
	if not username:
		redirect_url = secure_url(request, reverse('viewer:user_projects', kwargs={'username': request.user.username}))
		return HttpResponseRedirect(redirect_url)
	if username != request.user.username:
		if not request.user.is_superuser:
			return HttpResponse("Access Denied", content_type='text/plain', status=403)
		else:
			try:
				request.user = models.GislabUser.objects.get(username=username)
			except models.GislabUser.DoesNotExist:
				return HttpResponse("User does not exist.", content_type='text/plain', status=403)

	projects = [{
		'title': _('Empty Project'),
		'url': request.build_absolute_uri('/'),
	}]
	projects.extend(client.get_user_projects(request, username))
	context = {
		'username': username,
		'projects': projects,
		'debug': settings.DEBUG
	}
	return render(request, "viewer/user_projects.html", context, content_type="text/html")
