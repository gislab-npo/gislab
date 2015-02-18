# -*- coding: utf-8 -*-

from webgis.viewer.views import page


def mapjs(request):
	resp = page(request, "mobile/map.js")
	resp.content_type = "application/javascript"
	return resp
