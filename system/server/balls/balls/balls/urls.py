from django.conf.urls import patterns, url

urlpatterns = patterns("balls.balls.views",
	url(r"^$", "ball", name="ball"),
)
