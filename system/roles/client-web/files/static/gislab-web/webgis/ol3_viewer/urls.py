from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.ol3_viewer.views",
	url(r"^$", "app", name="app"),
)
