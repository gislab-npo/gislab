"""GIS.lab Management Library

User accounts administration

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.

.. sectionauthor:: Martin Landa <landa.martin gmail.com>
"""

import os
import re
import grp
import copy
import sys

from subprocess import call

import ldap
import ldap.modlist as modlist

from .utils import password_generate, \
     password_encrypt, read_vars_from_file
from .exception import GISLabAdminError
from .logger import GISLabAdminLogger

class GISLabUser(object):
    """GIS.lab user account.

    User account is initialized by create() or get() class methods.

    Throw GISLabAdminError on failure.
    """
    class MetaGISLabUser(type):
        def __init__(cls, name, bases, d):
            """Meta class constructor, opens LDAP connection.
            """
            type.__init__(cls, name, bases, d)
            
            cls._hooks = os.path.join('/', 'opt', 'gislab', 'system', 'account', 'hooks')
            
            # requires root
            if os.getuid() != 0:
                GISLabAdminLogger.error("This command can only be be run with superuser privileges")
                sys.exit(1)

            try:
                cls.ldap_base = "dc=gis,dc=lab"
                cls.ldap = ldap.initialize('ldapi:///')
                cls.ldap.protocol_version = ldap.VERSION3
                cls.ldap.simple_bind_s('cn=admin,{0}'.format(cls.ldap_base),
                                        open('/etc/gislab/gislab_ldap_admin_password.txt').read().rstrip('\n'))
                if cls.ldap is None:
                    raise GISLabAdminError()
            except ldap.LDAPError as e:
                raise GISLabAdminError("Unable to open LDAL connection: {}".format(e))

            GISLabAdminLogger.debug("LDAP connection established")

        def unbind(cls):
            """Close LDAL connection.
            """
            if cls.ldap:
                cls.ldap.unbind()
                cls.ldap = None
                GISLabAdminLogger.debug("LDAP connection closed")

        def _users_ldap(cls, query=None):
            """Get LDAP entries of GIS.lab users.

            Example:

            [('uid=lab1,ou=People,dc=gis,dc=lab', {'uid': ['lab1'], 'objectClass': ['inetOrgPerson', 'posixAccount', 'shadowAccount'], ...})]

            :param query: LDAP query to filter users or None to return all GIS.lab users

            :return: list of LDAP entries
            """
            if not query:
                # all gislab users
                gid = grp.getgrnam('gislabusers').gr_gid
                query = "(&(objectClass=inetOrgPerson)(gidNumber={}))".format(gid)
            
            ldap_items = cls.ldap.search_s(cls.ldap_base, ldap.SCOPE_SUBTREE, query)
            
            return ldap_items

    __metaclass__ = MetaGISLabUser

    def __init__(self, username, **kwargs):
        """
        GIS.lab user constuctor.

        :param username: user name (must be unique)
        :param kwargs: user attributes (firstname, lastname,
        ...), see create() for details
        """
        self.username = username

        # set prefix for logger
        self._log = "GISLabUser(%s): " % self.username
        
        # set user attributes
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
        self.fullname = "{0} {1}".format(self.firstname, self.lastname)
        self.home = os.path.join('/', 'mnt', 'home', self.username)
        self.published_data = os.path.join('/', 'storage', 'publish', self.username)
        
        # user/groupd id
        # gid must be defined before calling _next_uid()
        self.gid = int(grp.getgrnam('gislabusers').gr_gid)
        
    def _next_uid(self, min_uid=3000):
        """Get next free user ID.

        :param min_uid: starting uid
        
        :return: uid as integer
        """
        for item in self._get_users_ldap("(&(objectClass=inetOrgPerson)"
                                         "(gidNumber={}))".format(self.gid)):
            uid = int(item[1]['uidNumber'][0])
            if uid > min_uid:
                min_uid = uid
        
        min_uid += 1
        GISLabAdminLogger.debug("{0}uid={1}".format(self._log, min_uid))
        
        return min_uid
        
    @classmethod
    def create(cls, username, firstname, lastname, email,
               password, description, superuser):
        """Create a new GIS.lab user account.

        Throw GISLabAdminError when some account properties are invalid.

        :param username: user name (required)
        :param firstname: first name (required)
        :param lastname: last name (required)
        :param email: email (required) - must be unique
        :param password: password, if not given, it is automatically generated
        :param description: user description (optional)
        :param superuser: True to add user to superuser's group

        :return: GISLabUser object
        """
        # create new account
        user = cls(username, firstname=firstname, lastname=lastname,
                   email=email,
                   password=password, description=description,
                   superuser=superuser)
        
        # username/email validation
        if not user.is_username_valid():
            raise GISLabAdminError("Invalid characters in user name. "
                                   "User name can contain only lower "
                                   "case digits and numbers.")
        if not user.is_email_valid():
            raise GISLabAdminError("Invalid e-mail address format")
        if not user.is_email_unique():
            raise GISLabAdminError("User account e-mail must be unique. "
                                   "Account with this e-mail already "
                                   "exists.")
        
        GISLabAdminLogger.debug("{0}".format(user))

        # set uid
        user.uid = user._next_uid()

        # set user password or generated random password if not given
        if not password:
            user.set_password(password_generate())
        else:
            user.set_password(password)

        # create LDAP account
        user._create_ldap()

        # create PostgreSQL user account, publishing and credentials
        # hidden directories
        rc = call([os.path.join(user._hooks, 'adduser.sh'), username])
        GISLabAdminLogger.debug("{0}return code of adduser.sh: {1}".format(user._log, rc))
        if rc != 0:
            # rollback
            user._delete_ldap()
            raise GISLabAdminError("Unable to create a new GIS.lab user: "
                                   "adduser hook failed".format(username))
        
        return user

    @classmethod
    def list(cls, query=None):
        """List GIS.lab users.

        :param query: LDAP query to filter users or None to return all GIS.lab users

        :return: list of GISLabUser objects
        """
        # get admins
        try:
            items = cls._get_users_ldap('(&(objectClass=posixGroup)(cn=gislabadmins))')
            admins = items[0][1]['memberUid']
        except StandardError as e:
            raise GISLabAdminError("LDAP group 'gislabadmins' not found: {}".format(e))
        
        # list users
        users = []
        for ldap_item in cls._users_ldap(query):
            username = ldap_item[1]['uid'][0]
            data = ldap_item[1]
            user = cls(username, firstname=data['givenName'][0], lastname=data['sn'][0],
                       email=data['mail'][0], password=data['userPassword'][0],
                       description=data.get('description', [''])[0],
                       superuser=username in admins,
                       uid=int(data['uidNumber'][0]), gid=int(data['gidNumber'][0]),
                       home=data['homeDirectory'][0])
            users.append(user)

        return users

    @classmethod
    def get(cls, username):
        """Get GIS.lab user by name.

        Throw GISLabAdminError if user doesn't exists.

        :param username: GIS.lab user name

        :return: GISLabUser object
        """
        users = GISLabUser.list("(uid={})".format(username))
        if users is None or len(users) == 0:
            raise GISLabAdminError("GIS.lab user '{0}' doesn't "
                                   "exists".format(username))
        return users[0]

    @classmethod
    def _get_users_ldap(cls, query):
        return cls._users_ldap(query)

    @classmethod
    def exists(cls, username):
        """Check if GIS.lab user account exists.

        :param username: GIS.lab user name to be checked
        
        :return: True if user exists otherwise False
        """
        users = GISLabUser.list("(uid={})".format(username))
        if not users or len(users) != 1:
            return False
        
        return True

    def delete(self):
        """Delete GIS.lab user account.
        """
        if self.has_active_session():
            raise GISLabAdminError("GIS.lab user '{0}' is still running "
                              "session".format(self.username))
        
        # remove LDAP user
        self._delete_ldap()
        
        # drop PostgreSQL user, delete published data
        rc = call([os.path.join(self._hooks, 'deluser.sh'), self.username])
        GISLabAdminLogger.debug("{}return code of deluser.sh: {}".format(self._log, rc))
        if rc != 0:
            raise GISLabAdminError("Unable to delete GIS.lab user: "
                                   "deluser hook failed".format(username))
        
    def modify(self, **kwargs):
        """Modify GIS.lab user account.

        :param kwargs: user attributes to be changed, see create() for
        details
        """
        # open LDAP connection
        dn="uid={0},ou=people,{1}".format(self.username, self.ldap_base)

        # modify LDAP entries
        ldap_item = { 'firstname'  : 'givenName',
                      'lastname'   : 'sn',
                      'password'   : 'userPassword',
                      'email'      : 'mail',
                      'description': 'description' }

        # fullname changed ?
        old_fullname = None

        # superuser <-> normaluser changed ?
        superuser_changed = False
        if kwargs.get('superuser', None):
            superuser_changed = True
            self.superuser = not self.superuser
            kwargs.pop('superuser')

        # change other LDAP user attributes
        for key, value in kwargs.iteritems():
            if not value:
                continue # skip empty values

            if key == 'password': # password changed
                value = password_encrypt(value)
            elif key == 'email': # email changed
                if self.is_superuser():
                    # remove old mail from maildrop
                    self._remove_ldap_maildrop()
                # validate e-mail
                value = kwargs['email']
                if not self.is_email_valid(value):
                    raise GISLabAdminError("Invalid e-mail address format")
                if not self.is_email_unique(value):
                    raise GISLabAdminError("User account e-mail must be unique. "
                                           "Account with this e-mail already "
                                           "exists.")
            
            # set new user attribute, remember old value
            old_value = getattr(self, key)
            setattr(self, key, value)

            if key == 'email' and self.is_superuser():
                # add new mail to maildrop
                self._add_ldap_maildrop()

            # update full name if first or last name changed
            if key in ('firstname', 'lastname'):
                if not old_fullname:
                    old_fullname = self.fullname
                self.fullname = '{} {}'.format(self.firstname, self.lastname)

            # update LDAP attribute
            item = ldap_item[key]
            try:
                modlist = ldap.modlist.modifyModlist({item: [old_value]},
                                                     {item: [value]})
                self.ldap.modify_s(dn, modlist)
            except ldap.LDAPError as e:
                raise GISLabAdminError('{}'.format(e))

        # first or/and last name changed
        if old_fullname:
            for item in ('cn', 'gecos'):
                try:
                    modlist = ldap.modlist.modifyModlist({item: [old_fullname]},
                                                         {item: [self.fullname]})
                    self.ldap.modify_s(dn, modlist)
                except ldap.LDAPError as e:
                    raise GISLabAdminError('{}'.format(e))

        # superuser <-> normaluser changed
        if superuser_changed:
            if self.is_superuser():
                # normal -> superuser
                self._add_ldap_superuser()
                self._add_ldap_maildrop()
            else:
                # superuser -> normal
                self._remove_ldap_superuser()
                self._remove_ldap_maildrop()


    def __str__(self):
        """Get GIS.lab user string info.
        """
        user_str = "{0}:\n\tfirstname='{1}' lastname='{2}' email='{3}'" \
            "\n".format(self.username, self.firstname,
                        self.lastname, self.email)
        if self.description:
            user_str += "\tdescription='{0}'".format(self.description)
        user_str += "\tsuperuser={0}".format('yes' if self.superuser else 'no')
        if self.has_active_session():
            user_str += "\tis running a session"
            
        return user_str
    
    def is_username_valid(self):
        """Check if user name is valid

        :return: True if valid otherwise False
        """
        p = re.compile('^[a-z][a-z0-9_]*$')
        if not p.match(self.username):
            return False
        
        return True

    def is_email_valid(self, email=None):
        """Check if email is valid.

        :param email: e-mail to be validated or None to check already
        defined e-mail

	:return: True if valid otherwise False
        """
        if not email:
            email = self.email
        
        p = re.compile('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$')
        if not p.match(email):
            return False
        
        return True

    def is_email_unique(self, email=None):
        """Check if email is unique

        :param email: e-mail to be validated or None to check already
        defined e-mail

	:return: True if unique otherwise False
        """
        if not email:
            email = self.email
        
        gid = grp.getgrnam('gislabusers').gr_gid
        for ldap_item in self._get_users_ldap("(&(objectClass=inetOrgPerson)"
                                              "(gidNumber={}))".format(gid)):
            username = ldap_item[1]['uid'][0]
            usermail = ldap_item[1]['mail']
            if len(usermail) > 0 and username != self.username and \
                    usermail[0] == email:
                return False
        
        return True

    def set_password(self, password):
        """Set a new password for GIS.lab user.

        :param password: a new password to be set
        """
        self.password = password
        GISLabAdminLogger.debug("{0}new password='{1}'".format(self._log, self.password))

    def is_superuser(self):
        """Check if GIS.lab user is superuser.

        :return: True if user is superuser, otherwise return False
        """
        return self.superuser

    def has_active_session(self):
        """Check if user is running a session.

        :return: True if user is running a session otherwise False
        """
        return os.path.isfile(os.path.join(self.home, '.gislab', 'session.lock'))
        
    def _create_ldap(self):
        """Create record in LDAP database and activate forwarding of email
	sent to root if creating superuser account.

        Throw GISLabAdminError if password is not set or on encrypt failure.
        """
        # check password
        if not self.password:
            raise GISLabAdminError("Empty password")

        # encrypt password
        encrypted_password = password_encrypt(self.password)
        
        # define LDAP attributes
        dn="uid={0},ou=people,{1}".format(self.username, self.ldap_base)
        modlist = {
            "objectClass": ["inetOrgPerson", "posixAccount", "shadowAccount"],
            "uid": [self.username],
            "sn": [self.lastname],
            "givenName": [self.firstname],
            "cn": [self.fullname],
            "gecos": [self.fullname],
            "uidNumber": [str(self.uid)],
            "gidNumber": [str(self.gid)],
            "userPassword": [encrypted_password],
            "mail": [self.email],
            "loginShell": ["/bin/bash"],
            "homeDirectory": [self.home]
            }
        if self.description:
            modlist['description'] = self.description

        # add user to LDAP
        try:
            self.ldap.add_s(dn, ldap.modlist.addModlist(modlist))
        except ldap.LDAPError as e:
            raise GISLabAdminError('{}'.format(e))

        GISLabAdminLogger.debug("{0}Successfully set encoded password "
                           "for user {1}".format(self._log, dn))
        GISLabAdminLogger.debug("{0}Successfully added user '{1}' to "
                           "LDAP".format(self._log, self.username))

        # enable forwarding system mails for superuser
        if self.superuser:
            self._add_ldap_superuser()
            self._add_ldap_maildrop()

    def _add_ldap_superuser(self):
        """Add user to 'gislabadmins' group.
        """
        return self._add_ldap_group(['gislabadmins'])
    
    def _add_ldap_group(self, selected_groups = []):
        """Add user to LDAP groups

        :param selected_groups: list of groups from which user should be removed
        """
        for group in selected_groups:
            group_dn = 'cn={0},ou=Groups,{1}'.format(group, self.ldap_base)
            
            try:
                items = self._get_users_ldap('(&(objectClass=posixGroup)'
                                             '(cn={}))'.format(group))
                members_old = items[0][1]['memberUid']
            except StandardError as e:
                raise GISLabAdminError("LDAP group '{}' not found: {}".format(group, e))
            
            members_new = copy.deepcopy(members_old)
            if self.username not in members_old:
                members_new.append(self.username)
                group_modlist = ldap.modlist.modifyModlist({'memberUid': members_old},
                                                           {'memberUid': members_new})
                self.ldap.modify_s(group_dn, group_modlist)
                GISLabAdminLogger.debug("{0}Successfully added user '{1}' to group "
                                        "gislabadmins".format(self._log, self.username))
            else:
                GISLabAdminLogger.debug("User '{}' is already member of group "
                                        "gislabadmins".format(self.username))
        
    def _add_ldap_maildrop(self):
        """Enable forwarding of emails sent to root if user is superuser.
        """
        query = "(|(cn=root)(ou=MailAliases)({}))".format(self.ldap_base)
        result = self.ldap.search_s(self.ldap_base, ldap.SCOPE_SUBTREE, query)
        pfile = os.path.join('/',  'etc', 'postfix', 'sasl_passwd')
        if os.path.isfile(pfile) and result and len(result) == 1 and \
               self.email not in result[0][1]['maildrop']:
            old_value = result[0][1]['maildrop']
            new_value = copy.deepcopy(old_value)
            new.value.append(self.email)
            modlist = ldap.modlist.modifyModlist({'maildrop': old_value},
                                                 {'maildrop': new_value})
            dn = "cn=root,ou=MailAliases,{}".format(self.ldap_base)
            self.ldap.modify_s(dn, modlist)

            GISLabAdminLogger.debug("{0}Successfully added user {1} to root's "
                               "maildrop".format(self._log, self.username))
        
    def _delete_ldap(self):
        """Delete record from LDAP database.
        """
        dn="uid={0},ou=people,{1}".format(self.username, self.ldap_base)
        if self.superuser:
            # disable forwarding system mails to user if user was
            # superuser
            self._remove_ldap_maildrop()
            # remove user from all groups
            self._remove_ldap_group()

        # delete LDAP account
        try:
            self.ldap.delete_s(dn)
        except ldap.LDAPError as e:
            raise GISLabAdminError('{}'.format(e))

    def _remove_ldap_maildrop(self):
        """Disable forwarding of emails sent to root if user is superuser.
        """
        query = "(|(cn=root)(ou=MailAliases)({}))".format(self.ldap_base)
        result = self.ldap.search_s(self.ldap_base, ldap.SCOPE_SUBTREE, query)
        if result and len(result) == 1 and \
               self.email in result[0][1]['maildrop']:
            old_value = result[0][1]['maildrop']
            new_value = copy.deepcopy(old_value)
            new.value.remove(self.email)
            modlist = ldap.modlist.modifyModlist({'maildrop': old_value},
                                                 {'maildrop': new_value})
            dn = "cn=root,ou=MailAliases,{}".format(self.ldap_base)
            self.ldap.modify_s(dn, modlist)

            GISLabAdminLogger.debug("{0}Successfully removed user {1} from root's "
                               "maildrop".format(self._log, self.username))

    def _remove_ldap_superuser(self):
        """Remove user from 'gislabadmins' group.
        """
        return self._remove_ldap_group(['gislabadmins'])
    
    def _remove_ldap_group(self, selected_groups = []):
        """Remove user from LDAP groups.

        :param selected_groups: list of groups from which user should be removed
        """
        result = self._get_users_ldap("(&(objectClass=posixGroup))")
        for group in result:
            group_dn = group[0]
            group_name = group_dn[group_dn.find('cn'):].split(',', 1)[0].replace('cn=', '')
            if selected_groups and group_name not in selected_groups:
                continue
            if 'memberUid' not in group[1]:
                continue
            members = group[1]['memberUid']
            members_new = copy.deepcopy(members)
            if self.username in members_new:
                members_new.remove(self.username)
                group_modlist = ldap.modlist.modifyModlist({'memberUid': members},
                                                           {'memberUid': members_new})
                self.ldap.modify_s(group_dn, group_modlist)
                GISLabAdminLogger.debug("{0}Successfully removed user '{1}' from group "
                                        "{2}".format(self._log, self.username, group_name))
            else:
                GISLabAdminLogger.debug("{0}User '{1}' is not member of group "
                                        "{2}".format(self._log, self.username, group_name))
