# -*- coding: utf-8 -*-

import json
from django.shortcuts import render
from django.http import HttpResponse

from webgis.viewer.views import webgis_data


def mapjs(request):
	# TODO move it static
	context = {}
	return render(request, "mobile/map.js", context, content_type="application/javascript")

def map_config(request):
	data = webgis_data(request)
	data['user'] = {
		'username': request.user.username
	}
	data['layers'] = json.loads(data['layers'])
	data['base_layers'] = json.loads(data['base_layers'])
	data = '{0}({1})'.format(request.GET['callback'], json.dumps(data))
	return HttpResponse(data, "application/javascript")
