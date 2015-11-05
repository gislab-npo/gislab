from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.i18n import javascript_catalog
from django.conf.urls.static import static


js_info_dict = {
	'packages': ('webgis.viewer_old',),
}

urlpatterns = patterns('',
	url(r'', include('webgis.viewer_old.urls', namespace='viewer_old')),
	url(r'', include('webgis.storage.urls', namespace='storage')),
	url(r'^mobile/', include('webgis.mobile.urls', namespace='mobile')),
	url(r'^ol3/', include('webgis.viewer.urls', namespace='viewer')),
	url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
	url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
	url(r'^jsi18n/$', javascript_catalog, js_info_dict),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
