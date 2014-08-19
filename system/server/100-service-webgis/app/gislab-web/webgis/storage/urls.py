from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.storage.views",
	url(r"^ball/$", "ball", name="ball"),
	url(r"^drawing/$", "drawing", name="drawing"),
)
