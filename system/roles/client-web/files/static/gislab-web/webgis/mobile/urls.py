from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.mobile.views",
	url(r'^mobile/map.js$', 'mapjs', name='mapjs'),
	url(r'^mobile/config.json$', 'map_config', name='map_config'),
)
