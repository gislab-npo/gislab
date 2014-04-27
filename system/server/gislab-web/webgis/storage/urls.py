from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.storage.views",
	url(r"^$", "ball", name="ball"),
)
