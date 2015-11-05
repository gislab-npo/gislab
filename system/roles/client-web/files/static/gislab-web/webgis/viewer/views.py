# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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