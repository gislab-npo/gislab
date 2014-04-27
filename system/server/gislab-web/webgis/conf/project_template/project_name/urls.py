from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.i18n import javascript_catalog


js_info_dict = {
	'packages': ('webgis.viewer',),
}

urlpatterns = patterns('',
	url(r'', include('webgis.viewer.urls', namespace='viewer')),
	url(r'^ball/$', include('webgis.storage.urls', namespace='storage')),
	url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
	url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
	url(r'^jsi18n/$', javascript_catalog, js_info_dict),
)

urlpatterns += staticfiles_urlpatterns()
