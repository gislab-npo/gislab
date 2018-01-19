from django.conf.urls import include, url

from webgis.viewer.views import web_client
from webgis.userpage.views import user_projects
from .urls import urlpatterns as default_urlpatterns


def map_or_projects(request):
    if request.META.get('QUERY_STRING'):
        return web_client.map(request)
    # with redirect
    return user_projects(request, '')

    # without redirect
    # return user_projects(request, request.user.username)

urlpatterns = [url(r'^$', map_or_projects)] + default_urlpatterns
