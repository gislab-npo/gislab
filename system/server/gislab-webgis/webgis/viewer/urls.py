from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.viewer.views",
	url(r"^$", "page", name="page"),
	url("^featureinfo/$", "getfeatureinfo", name="featureinfo"),
	url("^print/$", "getprint", name="print"),
)
