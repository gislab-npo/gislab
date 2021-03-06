import os

from django.conf import settings


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


DEBUG = False

ROOT_URLCONF='djproject.urls_custom'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

GISQUICK_PROJECT_ROOT = '/publish/'
GISQUICK_MAPSERVER_URL = 'http://qgisserver:90/cgi-bin/qgis_mapserv.fcgi'


### DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data', 'gisquick.sqlite3'),
    }
}

INSTALLED_APPS = settings.INSTALLED_APPS + ('django_python3_ldap', )


### LDAP AUTHENTICATION ###
AUTHENTICATION_BACKENDS = (
    'django_python3_ldap.auth.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)


LDAP_AUTH_URL = "ldap://172.17.0.1:389"

LDAP_AUTH_USE_TLS = True


LDAP_AUTH_SEARCH_BASE = "ou=people,dc=gis,dc=lab"
# AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=people,dc=gis,dc=lab", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# or perhaps:
#AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=people,dc=gis,dc=lab"

# AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=gis,dc=lab", ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)")
# AUTH_LDAP_GROUP_TYPE = PosixGroupType()
# AUTH_LDAP_REQUIRE_GROUP = "cn=gislabusers,ou=groups,dc=gis,dc=lab"

LDAP_AUTH_USER_FIELDS = {
    "username": "uid",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_active": "cn=gislabusers,ou=groups,dc=gis,dc=lab",
#     "is_staff": "cn=gislabadmins,ou=groups,dc=gis,dc=lab",
#     "is_superuser": "cn=gislabadmins,ou=groups,dc=gis,dc=lab"
# }

# AUTH_LDAP_GLOBAL_OPTIONS = {
#     ldap.OPT_X_TLS_REQUIRE_CERT: False,
# }

# AUTH_LDAP_ALWAYS_UPDATE_USER = True
# AUTH_LDAP_FIND_GROUP_PERMS = True
# AUTH_LDAP_CACHE_GROUPS = True
# AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }
    },
    "loggers": {
        "django_python3_ldap": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
}
