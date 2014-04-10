"""
Django settings for WebGIS project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


### DEBUG ###
DEBUG = False
TEMPLATE_DEBUG = False


### WebGIS SETTINGS ###
WEBGIS_PROJECTS_ROOT = '/storage/share/'
WEBGIS_OWS_URL = 'http://server.gis.lab/cgi-bin/qgis_mapserv.fcgi'
WEBGIS_SCALES = (10000000,5000000,2500000,1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500)
WEBGIS_GUEST_USERNAME = 'guest'

# Dictionary of <MIME Type>: <File extension> pairs
FILE_EXTENSIONS_TABLE = {
	"application/json": "json",
	"application/geojson": "geojson",
}

ALLOWED_HOSTS = ['web.gis.lab']


### INTERNATIONALIZATION ###
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Bratislava'
USE_I18N = True
USE_L10N = True
USE_TZ = True


### OTHER ###
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
)

INSTALLED_APPS = (
	'django.contrib.staticfiles',
	'webgis.viewer',
	'webgis.storage',
)

ROOT_URLCONF = '{{ project_name }}.urls'
WSGI_APPLICATION = '{{ project_name }}.wsgi.application'

LOGIN_URL = '/login/'
AUTH_USER_MODEL = 'viewer.GislabUser'


#import secret settings
try:
	from settings_secret import *
except ImportError:
	pass

from settings_ldap import *

# vim: set syntax=sh ts=4 sts=4 sw=4 noet
