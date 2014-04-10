import ldap

from django_auth_ldap.config import LDAPSearch, PosixGroupType


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
