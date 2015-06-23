"""GIS.lab Management Library

Top level administration

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.

.. sectionauthor:: Martin Landa <landa.martin gmail.com>
"""

import os
import ldap
import grp
import re

from .user import GISLabUser
from .exception import GISLabAdminError
from .logger import GISLabAdminLogger


class GISLabAdmin(object):
    """Main class.

    Throw GISLabAdminError on failure.
    """
    class MetaGISLabAdmin(type):
      def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)
        cls.policy_file = os.path.join('/', 'etc' , 'gislab',
                                     'gislab_unknown_machines_policy.conf')
        cls.known_machines_list_file = os.path.join('/', 'etc', 'gislab',
                                                    'gislab_known_machines.txt')
        cls.known_machines_dhcp_file = os.path.join('/', 'etc', 'dhcp',
                                                    'gislab_known_machines.conf')

    __metaclass__ = MetaGISLabAdmin

    @staticmethod
    def user_add(username, **kwargs):
        """Create new GIS.lab user account.

        Throw GISLabAdminError if user already exists.

        :param username: user name
        :param kwargs: user attributes, see GISLabUser.create() for details

        :return: GISLabUser object
        """
        return GISLabUser.create(username, **kwargs)

    @staticmethod
    def user_delete(username):
        """Delete existing GIS.lab user account.

	Throw GISLabAdminError if user doesn't exists.

        :param username: user name
        """
        GISLabUser.get(username).delete()

    @staticmethod
    def user_modify(username, **kwargs):
        """Modify existing GIS.lab user account.

        Throw GISLabAdminError if user doesn't exists.

        :param username: user name
        :param kwargs: user attributes, see GISLabUser.create() for details
        """
        GISLabUser.get(username).modify(**kwargs)

    @staticmethod
    def users():
        """Get list of GIS.lab user accounts.

        :return: list of GISLabUser objects
        """
        return GISLabUser.users()

    @staticmethod
    def user_get(username):
        """Get GIS.lab user object.

        Throw GISLabAdminError if user doesn't exists.

        :param username: user name

        :return: GISLabUser object
        """
        return GISLabUser.get(username)

    @staticmethod
    def user_backup(username):
        """Backup GIS.lab user account.

        Throw GISLabAdminError if user doesn't exists.

        :param username: user name
        """
        GISLabUser.get(username).backup()

    @staticmethod
    def user_restore(username):
        """Restore GIS.lab user account from backup.

        Throw GISLabAdminError if user already exists.

        :param username: user name

        :return: GISLabUser object
        """
        return GISLabUser.restore(username)

    @staticmethod
    def machine_add(mac):
        """Add machine to list of known GIS.lab machines.

        :todo: to be implemented

        :param mac: MAC address
        """
        if mac == 'all':
            pass # TODO
        else:
            p = re.compile('^[0-9a-zA-Z]{2}:[0-9a-zA-Z]{2}:[0-9a-zA-Z]{2}:[0-9a-zA-Z]{2}:[0-9a-zA-Z]{2}:[0-9a-zA-Z]{2}$')
            if not p.match(mac):
                raise GISLabAdminError("Skipping MAC address {} - invalid format".format(mac))

            GISLabAdminLogger.info("Adding MAC address {}".format(mac))
            # add records to known machines list file in /etc/gislab

    @staticmethod
    def machine_delete(mac):
        """Remove machine from list of known GIS.lab machines.

        :todo: to be implemented

        :param mac: MAC address
        """
        pass

    @classmethod
    def machines(cls):
        """Get list of known GIS.lab machines.

        :return: list of MAC addresses
        """
        try:
            with open(cls.known_machines_list_file) as f:
                return f.read().splitlines()
        except IOError as e:
            raise GISLabAdminError(str(e))

    @classmethod
    def machine_policy(cls):
        """Get current GIS.lab unknown machines policy.

        :return: policy as string (allow or deny)
        """
        try:
            with open(cls.policy_file) as f:
                return f.read().rstrip('\n')
        except IOError as e:
            raise GISLabAdminError(str(e))
