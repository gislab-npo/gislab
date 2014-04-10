from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = patterns('',
	url(r'', include('webgis.viewer.urls', namespace='viewer')),
	url(r'^ball/$', include('webgis.storage.urls', namespace='storage')),
	url(r'^login/$', "django.contrib.auth.views.login", name="login"),
	url(r'^logout/$', "django.contrib.auth.views.logout", name="logout"),
)

urlpatterns += staticfiles_urlpatterns()
