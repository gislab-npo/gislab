"""
Django settings for GIS.lab Web.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os

import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


### DEBUG ###
DEBUG = False
TEMPLATE_DEBUG = False


### GIS.lab Web SETTINGS ###
WEBGIS_PROJECT_ROOT = '/mnt/share/'
WEBGIS_MAPSERVER_URL = 'http://ms.gis.lab:90/cgi-bin/qgis_mapserv.fcgi'
WEBGIS_GUEST_USERNAME = 'guest'

# Dictionary of <MIME Type>: <File extension> pairs
FILE_EXTENSIONS_TABLE = {
	"application/json": "json",
	"application/geojson": "geojson",
}

ALLOWED_HOSTS = ['*']

### LDAP Authentication ###

# Keep ModelBackend around for guest user, per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
	'django_auth_ldap.backend.LDAPBackend',
	'django.contrib.auth.backends.ModelBackend',
)

# Baseline configuration.
#AUTH_LDAP_SERVER_URI = ""
AUTH_LDAP_START_TLS = True

AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=people,dc=gis,dc=lab", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# or perhaps:
#AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=people,dc=gis,dc=lab"

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=gis,dc=lab", ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)")
AUTH_LDAP_GROUP_TYPE = PosixGroupType()
# Only users in this group can log in.
AUTH_LDAP_REQUIRE_GROUP = "cn=labusers,ou=groups,dc=gis,dc=lab"

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
	"first_name": "givenName",
	"last_name": "sn",
	"email": "mail"
}
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
	"is_active": "cn=labusers,ou=groups,dc=gis,dc=lab",
	"is_staff": "cn=labadmins,ou=groups,dc=gis,dc=lab",
	"is_superuser": "cn=labadmins,ou=groups,dc=gis,dc=lab"
}

AUTH_LDAP_GLOBAL_OPTIONS = {
	ldap.OPT_X_TLS_REQUIRE_CERT: False,
	#ldap.OPT_X_TLS_NEVER: 1
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True
# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True
# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

#import logging
#logger = logging.getLogger('django_auth_ldap')
#logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)


### INTERNATIONALIZATION ###
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGES = (
	('sk', u'Slovak'),
	('en-us', u'English'),
)
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

MEDIA_URL = '/media/'

if os.path.exists('/storage/webgis-media'):
	MEDIA_ROOT = '/storage/webgis-media'
else:
	MEDIA_ROOT =  os.path.join(BASE_DIR, 'media/')

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.staticfiles',
	'webgis.viewer',
	'webgis.storage',
	'webgis.mapcache',
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

# vim: set syntax=sh ts=4 sts=4 sw=4 noet
