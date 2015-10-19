# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from webgis.mobile import forms
from webgis.viewer.views import WebClient
from webgis.viewer.client import LoginRequired


class MobileClient(WebClient):

	def get_ows_url(self, request):
		return request.build_absolute_uri(super(MobileClient, self).get_ows_url(request))

	def get_mapcache_tile_url(self, request):
		return request.build_absolute_uri(super(MobileClient, self).get_mapcache_tile_url(request))

	def get_mapcache_legend_url(self, request):
		return request.build_absolute_uri(super(MobileClient, self).get_mapcache_legend_url(request))

	def get_vectorlayers_url(self, request):
		return request.build_absolute_uri(super(MobileClient, self).get_vectorlayers_url(request))


	def render(self, request, project_data):
		return HttpResponse(json.dumps(project_data), content_type="application/json")

client = MobileClient()


def project_config(request):
	try:
		return client.project_request(request)
	except LoginRequired, e:
		return HttpResponse('Authentication required', status=401)


@csrf_exempt
def client_login(request):
	if request.method == 'POST':
		#data = json.loads(request.body)
		#print data
		#form = forms.LoginForm(data)
		form = forms.LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user:
				try:
					login(request, user)
				except Exception, e:
					print e
				return HttpResponse(status=200)
	logout(request)
	return HttpResponse(status=401)

def client_logout(request):
	logout(request)
	return HttpResponse(status=200)
