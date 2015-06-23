"""GIS.lab Management Library

User accounts administration

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.

.. sectionauthor:: Martin Landa <landa.martin gmail.com>
"""

import os
import re
import pwd
import grp
import shutil
import copy
import fileinput
import tarfile
import glob
import sys

from datetime import datetime
from subprocess import call

import ldap
import ldap.modlist as modlist

from .utils import nextuid, password_generate, \
     password_encrypt, password_validate, read_env
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

        def _unbind(cls):
            """Close LDAL connection.
            """
            cls.ldap.unbind()
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

        def _admins(cls):
            """Get GIS.lab superuser names.

            Example: 

            ['gislab', ...]
            
            :return: list of usernames
            """
            query = "(&(objectClass=posixGroup)(cn=gislabadmins))"
            result = cls.ldap.search_s(cls.ldap_base, ldap.SCOPE_SUBTREE, query)
            if result is None and len(result) != 1:
                raise GISLabAdminError("User group 'gislabadmins not found")
            
            return result[0][1]['memberUid']

    __metaclass__ = MetaGISLabUser

    def __init__(self, username, **kwargs):
        """
        Throw GISLabAdminError when user name is not valid. User name can
        contain only lower case digits and numbers.

        :param username: user name (must be unique)
        :param kwargs: user attributes (firstname, lastname,
        ...), see create() for details
        """
        # do user name validation
        self.username = self._validate_username(username)

        # set user attributes
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
        self.fullname = "{0} {1}".format(self.firstname, self.lastname)
        self.home = os.path.join('/', 'mnt', 'home', self.username)
        self.published_data = os.path.join('/', 'storage', 'publish', self.username)

        # set prefix for logger
        self._log = "GISLabUser(%s): " % self.username

    @classmethod
    def __del__(cls):
        """Class destructor.

        Close LDAP connection.
        """
        cls._unbind()
        
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
        # check if user account already exists
        try:
            pwd.getpwnam(username)
            raise GISLabAdminError("GIS.lab user '{0}' already exists".format(username))
        except KeyError:
            pass

        # create new account
        user = cls(username, firstname=firstname, lastname=lastname,
                   email=email,
                   password=password, description=description,
                   superuser=superuser,
                   uid=nextuid(),
                   gid = int(grp.getgrnam('gislabusers').gr_gid))
        # do e-mail validation
        user._validate_email(email)

        GISLabAdminLogger.debug("{0}".format(user))

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
    def users(cls, query=None):
        """Get list of GIS.lab users.

        :param query: LDAP query to filter users or None to return all GIS.lab users

        :return: list of GISLabUser objects
        """
        # get admins
        admins = cls._admins()

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
        query = "(uid={})".format(username)
        users = GISLabUser.users(query)
        if users is None or len(users) == 0:
            raise GISLabAdminError("GIS.lab user '{}' doesn't exists".format(username))
        return users[0]

    @classmethod
    def _get_users_ldap(cls, query):
        return cls._users_ldap(query)

    @classmethod
    def _get_admins(cls):
        return cls._admins()

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
                value = self._validate_email(kwargs['email'])

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
                raise GISLabAdminError(str(e))

        # first or/and last name changed
        if old_fullname:
            for item in ('cn', 'gecos'):
                try:
                    modlist = ldap.modlist.modifyModlist({item: [old_fullname]},
                                                         {item: [self.fullname]})
                    self.ldap.modify_s(dn, modlist)
                except ldap.LDAPError as e:
                    raise GISLabAdminError(str(e))

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

    def backup(self):
        """Backup GIS.lab user account.

        :param username: GIS.lab user name
        """
        # read GIS.lab environment variables
        read_env(os.path.join('/', 'etc', 'gislab_version'))

        # backup settings
        backup_dir = os.path.join('/', 'storage', 'backup')
        date = "{:%Y-%m-%d:%H-%M-%S}".format(datetime.now())
        temp_backup_dir = os.path.join('/', 'tmp',
                                       'gislab-{0}-{1}'.format(self.username, date))
        home_backup_file = os.path.join(temp_backup_dir, 'home.tar.bz2')
        publish_backup_file = os.path.join(temp_backup_dir, 'publish.tar.bz2')
        db_backup_file = os.path.join(temp_backup_dir, 'postgresql.dump')
        ldap_backup_file = os.path.join(temp_backup_dir, 'ldap.dump')
        backup_file = os.path.join(backup_dir, 'gislab-{0}-{1}.tar'.format(self.username, date))

        # create backup directory if not exists
        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)
            os.chmod(backup_dir, 0o700)

        # create tmp backup directory
        os.mkdir(temp_backup_dir)

        # write GIS.lab version
        with open(os.path.join(temp_backup_dir, 'GISLAB_VERSION'), 'w') as f:
            f.write(os.environ['GISLAB_VERSION'] + '\n')

        # backup home directory and published data
        self._backup_dirs(home_backup_file, publish_backup_file)

        # backup PostgreSQL data
        self._backup_postgres(db_backup_file)

        # backup LDAP data
        ldap_item = self._get_users_ldap("uid={}".format(self.username))
        if ldap_item is None or len(ldap_item) == 0:
            raise GISLabAdminError("No LDAP entry for GIS.lab user '{}'".format(self.username))
        self._backup_ldap(ldap_item[0], ldap_backup_file)

        # create backup file
        with tarfile.open(backup_file, "w") as tar:
            tar.add(temp_backup_dir, arcname='.')
        os.chmod(backup_file, 0o400)

        GISLabAdminLogger.info("{0}: Backup stored in {1}".format(self._log, backup_file))

        # clean up
        shutil.rmtree(temp_backup_dir)

    @classmethod
    def restore(cls, username):
        """Backup user account.

        :todo: To be implemented

        :param username: user name
        """
        pass

    def _backup_ldap(self, ldap_user, ldap_backup_file):
        """Backup LDAP user data

        :todo: userPassword differs from ldapfinger (why?)

        :param ldap_user: LDAL entry
        :param ldap_backup_file: full path to LDAP dump file
        """
        with open(ldap_backup_file, 'w') as f:
            f.write('dn: {}\n'.format(ldap_user[0]))
            for key, values in ldap_user[1].iteritems():
                for v in map(lambda x: x.rstrip('\n'), values):
                    f.write('{0}: {1}\n'.format(key, v))

                if self.is_superuser():
                    f.write("\n#superuser\n")

    def _backup_dirs(self, home_backup_file, publish_backup_file):
        """Backup GIS.lab user home directory.

        Load home directory names from XDG.

        :param home_backup_file: full path to home tarball
        :param publish_backup_file: full path to published data tarball
        """
        # define exclude from user-dirs.dirs if exists
        dirs_file = os.path.join(self.home, '.config', 'user-dirs.dirs')
        exclude = None
        if os.path.isfile(dirs_file):
            read_env(dirs_file)
            exclude = os.path.join(self.home, os.path.basename(os.environ['XDG_DOWNLOAD_DIR']))

        # create tarball
        with tarfile.open(home_backup_file, "w:bz2") as tar:
            def excludes_fn(info):
                name = info.name
                return name.startswith('.*') or \
                       name.startswith('Barrel') or \
                       name.startswith('Booster') or \
                       name.startswith('Publish') or \
                       name.startswith('Repository') or \
                       (exclude and exclude in name)
            try:
                tar.add(self.home, filter=excludes_fn)
            except OSError as e:
                raise GISLabAdminError(e)

            for f in glob.glob(os.path.join(self.home, '.config', 'user-dirs.*')):
                tar.add(f)

            # QGIS
            qgis_file = os.path.join(self.home, '.config', 'QGIS', 'QGIS2.conf')
            if os.path.exists(qgis_file):
                tar.add(qgis_file)

            for f in glob.glob(os.path.join(self.home, '.qgis2', '*.db')):
                tar.add(f)

            # GRASS
            for d in (os.path.join(self.home, '.grass7'),
                      os.path.join(self.home, '.grassdata')):
                if os.path.exists(d):
                    tar.add(d)

        # backup published projects
        with tarfile.open(publish_backup_file, "w:bz2") as tar:
            tar.add(self.published_data)

    def _backup_postgres(self, db_backup_file):
        """Backup GIS.lab user database data.

        :param db_backup_file: full path to PG dump file
        """
        # open connection and cursor
        con = connect(user='postgres', dbname='gislab', password='gislab')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        # prepare data for backup
        try:
            cur.execute("DROP TABLE IF EXISTS {}.gislab_ball".format(self.username))
            cur.execute("DROP TABLE IF EXISTS {}.gislab_drawing".format(self.username))
            cur.execute("CREATE TABLE {0}.gislab_ball AS SELECT * FROM storage_ball "
                        "WHERE \"user\" = '{0}'".format(self.username))
            cur.execute("CREATE TABLE {0}.gislab_drawing AS SELECT * FROM "
                        "storage_drawing WHERE \"user\" = '{0}'".format(self.username))
        except ProgrammingError as e:
            raise GISLabAdminError("PostgreSQL: {0}".format(e).rstrip("\n"))
        cur.close()

        # create PG dump
        call(['pg_dump', '-U', 'postgres', '-Fc', '--schema={}'.format(self.username),
              '-f', db_backup_file, 'gislab'])

        # clean up - remove support tables
        cur = con.cursor()
        try:
            cur.execute("DROP TABLE {}.gislab_ball".format(self.username))
            cur.execute("DROP TABLE {}.gislab_drawing".format(self.username))
        except ProgrammingError as e:
            raise GISLabAdminError("PostgreSQL: {0}".format(e).rstrip("\n"))

        # close cursor and connection
        cur.close()
        con.close()

    def __str__(self):
        """Get GIS.lab user string info.
        """
        return "GISLabUser({0}): firstname='{1}' lastname='{2}' email='{3}' description='{4}' " \
               "superuser={5} has_active_session={6}".format(self.username, self.firstname,
                                                    self.lastname, self.email,
                                                    self.description, self.superuser,
                                                    self.has_active_session())

    def _validate_username(self, username):
        """Perform user name validation.

        :param username: GIS.lab user name

        Throws GISLabAdminError when user name is not valid

        :return: validated username
        """
        p = re.compile('^[a-z][a-z0-9_]*$')
        if not p.match(username):
            raise GISLabAdminError("Invalid characters in user name."
                              "User name can contain only lower "
                              "case digits and numbers.")

        return username

    def _validate_email(self, email):
        """Perform email validation.

        :param email: email address

        Throws GISLabAdminError when email is not valid

	:return: validated email
        """
        # validate
        p = re.compile('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$')
        if not p.match(email):
            raise GISLabAdminError("Invalid e-mail address format")

        # check if email is unique
        gid = grp.getgrnam('gislabusers').gr_gid
        query = "(&(objectClass=inetOrgPerson)(gidNumber={}))".format(gid)
        for ldap_item in self.ldap.search_s(self.ldap_base, ldap.SCOPE_SUBTREE, query):
            username = ldap_item[1]['uid'][0]
            usermail = ldap_item[1]['mail']
            if len(usermail) > 0 and username != self.username and usermail[0] == email:
                raise GISLabAdminError("User account with this e-mail address already "
                                  "exists ({})".format(username))

        return email

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
        ret = os.path.isfile(os.path.join(self.home, '.gislab', 'session.lock'))
        GISLabAdminLogger.debug("{0}has_active_session='{1}'".format(self._log, ret))
        
        return ret

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
        if password_validate(encrypted_password, self.password) is False:
            raise GISLabAdminError("Validation of encrypted password failed")

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
            raise GISLabAdminError(str(e))

        GISLabAdminLogger.debug("{0}Successfully set encoded password "
                           "for user {1}".format(self._log, dn))
        GISLabAdminLogger.debug("{0}Successfully added user '{1}' to "
                           "LDAP".format(self._log, self.username))

        # enable forwarding system mails for superuser
        if self.superuser:
            self._add_ldap_superuser()
            self._add_ldap_maildrop()

    def _add_ldap_superuser(self):
        """Add user to 'gislabadmins' group,
        """
        group_dn="cn=gislabadmins,ou=Groups,{1}".format(self.username, self.ldap_base)
        admins = self._get_admins()
        new_admins = copy.deepcopy(admins)
        if self.username not in new_admins:
            new_admins.append(self.username)
            group_modlist = ldap.modlist.modifyModlist({'memberUid': admins},
                                                       {'memberUid': new_admins})
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
            raise GISLabAdminError(str(e))

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
        """Remove user from gislabadmins group
        """
        return self._remove_ldap_group(['cn=gislabadmins,ou=Groups,dc=gis,dc=lab'])
    
    def _remove_ldap_group(self, selected_groups = []):
        """Remove user from LDAP groups.
        """
        query = "(&(objectClass=posixGroup))"
        result = self.ldap.search_s(self.ldap_base, ldap.SCOPE_SUBTREE, query)
        for group in result:
            group_dn = group[0]
            if selected_groups and group_dn not in selected_groups:
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
                                   "{2}".format(self._log, self.username, group_dn))
            else:
                GISLabAdminLogger.debug("{0}User '{1}' is not member of group "
                                   "{2}".format(self._log, self.username, group_dn))
