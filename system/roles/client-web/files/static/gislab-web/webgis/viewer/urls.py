from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.viewer.views",
	url(r"^$", "app", name="app"),
	url(r"^filter/$", "filter", name="filter"),
)
