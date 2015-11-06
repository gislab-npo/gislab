# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

#from owslib.wfs import WebFeatureService


def app(request):
	data = {
		'project': request.GET['PROJECT']
	}
	return render(
		request,
		"viewer/index.html",
		data,
		content_type="text/html"
	)

def filter(request):
    url = settings.GISLAB_WEB_MAPSERVER_URL
    path = settings.GISLAB_WEB_PROJECT_ROOT
    project = request.GET['PROJECT']
    print url, project
    print url + "?MAP=" + path + project + "&service=wms&request=getcapabilities"
    return HttpResponse('{"Ahoj":"svete"}', content_type="application/json")
