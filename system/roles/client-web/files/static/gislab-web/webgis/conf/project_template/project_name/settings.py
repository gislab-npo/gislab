"""
Django settings for GIS.lab Web.
"""

import os

import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


### DEBUG ###
DEBUG = False
TEMPLATE_DEBUG = False


### GIS.lab Web ###
GISLAB_WEB_PROJECT_ROOT = '/mnt/publish/'
GISLAB_WEB_MAPSERVER_URL = 'http://ms.gis.lab:90/cgi-bin/qgis_mapserv.fcgi'
GISLAB_WEB_GUEST_USERNAME = 'guest'

# Dictionary of <MIME Type>: <File extension> pairs
FILE_EXTENSIONS_TABLE = {
	"application/json": "json",
	"application/geojson": "geojson",
}


### INTERNATIONALIZATION ###
LANGUAGES = (
	('sk', u'Slovak'),
	('en-us', u'English'),
)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Bratislava'
USE_I18N = True
USE_L10N = True
USE_TZ = True


### LDAP AUTHENTICATION ###
AUTHENTICATION_BACKENDS = (
	'django_auth_ldap.backend.LDAPBackend',
	'django.contrib.auth.backends.ModelBackend',
)
AUTH_LDAP_START_TLS = True

AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=people,dc=gis,dc=lab", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# or perhaps:
#AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=people,dc=gis,dc=lab"

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=gis,dc=lab", ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)")
AUTH_LDAP_GROUP_TYPE = PosixGroupType()
AUTH_LDAP_REQUIRE_GROUP = "cn=gislabusers,ou=groups,dc=gis,dc=lab"

AUTH_LDAP_USER_ATTR_MAP = {
	"first_name": "givenName",
	"last_name": "sn",
	"email": "mail"
}
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
	"is_active": "cn=gislabusers,ou=groups,dc=gis,dc=lab",
	"is_staff": "cn=gislabadmins,ou=groups,dc=gis,dc=lab",
	"is_superuser": "cn=gislabadmins,ou=groups,dc=gis,dc=lab"
}

AUTH_LDAP_GLOBAL_OPTIONS = {
	ldap.OPT_X_TLS_REQUIRE_CERT: False,
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600


### OTHER ###
ALLOWED_HOSTS = ['*']

# Enable CORS requests
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'

if os.path.exists('/storage/applications/gislab-web/media'):
	MEDIA_ROOT = '/storage/applications/gislab-web/media'
else:
	MEDIA_ROOT =  os.path.join(BASE_DIR, 'media/')

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'webgis.libs.middleware.GislabHeaderMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
)

INSTALLED_APPS = (
	'corsheaders',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.staticfiles',
	'webgis.viewer',
	'webgis.storage',
	'webgis.mapcache',
	'webgis.mobile',
)

ROOT_URLCONF = '{{ project_name }}.urls'
WSGI_APPLICATION = '{{ project_name }}.wsgi.application'

LOGIN_URL = '/login/'
AUTH_USER_MODEL = 'viewer.GislabUser'


# import secret settings
try:
	from settings_secret import *
except ImportError:
	pass


# vim: set syntax=sh ts=4 sts=4 sw=4 noet
