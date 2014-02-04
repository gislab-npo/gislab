from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = patterns('',
	url(r'', include('webgis.viewer.urls')),
	url(r'^ball/$', include('webgis.storage.urls')),
)

urlpatterns += staticfiles_urlpatterns()
