from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.mobile.views",
	url(r"^login/$", "client_login", name="client_login"),
	url(r"^logout/$", "client_logout", name="client_logout"),
	url(r"^config.json$", "project_config", name="project_config"),
)
