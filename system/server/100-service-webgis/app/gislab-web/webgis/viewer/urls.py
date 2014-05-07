from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.viewer.views",
	url(r"^$", "page", name="page"),
	url("^owsrequest/$", "ows_request", name="owsrequest"),
	url("^tile/(?P<project>.*)/(?P<publish>\d+)/1.0.0/(?P<layers>[^/]+)/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)\.(?P<format>\w+)$", "tile", name="tile"),
)
