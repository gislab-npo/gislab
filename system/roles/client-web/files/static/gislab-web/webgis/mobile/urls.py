from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.mobile.views",
	url(r'^mobile/map.js$', 'mapjs', name='mapjs'),
)
