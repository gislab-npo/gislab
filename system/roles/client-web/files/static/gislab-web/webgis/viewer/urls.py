from django.conf.urls import patterns, url

urlpatterns = patterns("webgis.viewer.views",
	url(r"^$", "page", name="page"),
	url(r"^user/(?P<username>[^/]*)/?$", "user_projects", name="user_projects"),
	url("^owsrequest/$", "ows_request", name="owsrequest"),
	url("^tile/(?P<project_hash>[^/]+)/(?P<publish>\d+)/tile/(?P<layers_hash>[^/]+)/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)\.(?P<format>\w+)$", "tile", name="tile"),
	url("^legend/(?P<project_hash>[^/]+)/(?P<publish>\d+)/legend/(?P<layer_hash>[^/]+)/(?P<zoom>\d+)\.(?P<format>\w+)$", "legend", name="legend"),
	url("^vector/$", "vector_layers", name="vectorlayers"),

	url("^gislab_version.json$", "gislab_version_json", name="gislab_version_json"),
	url("^user.json$", "user_json", name="user_json"),
	url("^projects.json$", "projects_json", name="projects_json"),
	url("^drawings.json$", "drawings_json", name="drawings_json"),
)
