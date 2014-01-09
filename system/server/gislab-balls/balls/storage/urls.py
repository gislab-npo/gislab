from django.conf.urls import patterns, url

urlpatterns = patterns("balls.storage.views",
	url(r"^$", "ball", name="ball"),
)
