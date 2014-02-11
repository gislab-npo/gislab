from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.viewer.views",
	url(r"^$", "page", name="page"),
	url("^featureinfo/$", "featureinfo", name="featureinfo"),
	url("^print/$", "getprint", name="getprint"),
)
