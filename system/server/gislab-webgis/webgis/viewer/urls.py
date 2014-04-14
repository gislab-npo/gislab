from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.viewer.views",
	url(r"^$", "page", name="page"),
	url("^owsrequest/$", "ows_request", name="owsrequest"),
)
