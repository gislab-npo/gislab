"""GIS.lab Administration Management Library

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.

:todo: To be implement:

 - GISLabUser.is_connected()
 - GISLabUser.restore()
 - GISLab.machine_add()
 - GISLab.machine_delete()

.. sectionauthor:: Martin Landa <landa.martin gmail.com>
"""

import os
import ldap
import grp
import re

from user import GISLabUser
from exception import GISLabAdminError
from logger import GISLabAdminLogger

class GISLabAdmin(object):
    """Main GIS.lab class.

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

         - create LDAP user account
         - enable forwarding system mails (only for superusers)
         - create PostgreSQL user account
         - create publishing directory
         - save user credentials to hidden directory in home folder

        Throw GISLabAdminError if user already exists.

        :param username: GIS.lab user name account to be added
        :param kwargs: user attributes, see GISLabUser.create() for details
        
        :return: GISLabUser
        """
        return GISLabUser.create(username, **kwargs)
        
    @staticmethod
    def user_delete(username):
        """Delete existing GIS.lab user account.

         - delete user home
         - delete LDAP user account
         - delete PostgreSQL user account
         - delete published data
         
        Throw GISLabAdminError if user doesn't exists.

        :param username: GIS.lab user name account to be deleted
        """
        GISLabUser.get(username).delete()

    @staticmethod
    def user_modify(username, **kwargs):
        """Modify existing GIS.lab user account.

        Throw GISLabAdminError if user doesn't exists.

        :param username: GIS.lab user name account to be modified
        :param kwargs: user attributes, see GISLabUser.create() for details
        """
        GISLabUser.get(username).modify(**kwargs)
    
    @staticmethod
    def users():
        """List GIS.lab user accounts.

        :return: list of GISLabUser objects
        """
        return GISLabUser.users()

    @staticmethod
    def user_get(username):
        """Get GISLab user account.

        Throw GISLabAdminError if user doesn't exists.

        :param username: GIS.lab user name account

        :return: GISLabUser
        """
        return GISLabUser.get(username)

    @staticmethod
    def user_backup(username):
        """Backup GISLab user account.

        Throw GISLabAdminError if user doesn't exists.

        :param username: GIS.lab user name account to be backuped
        """
        GISLabUser.get(username).backup()

    @staticmethod
    def user_restore(username):
        """Restore GISLab user account from backup.

        Throw GISLabAdminError if user already exists.

        :param username: GIS.lab user name account to be restored

        :return: GISLabUser
        """
        return GISLabUser.restore(username)

    @staticmethod
    def machine_add(mac):
        """Add GIS.lab client machine to list of known machines.

        :todo: to be implemented

        :param mac: MAC address to be added or 'all' to change policy
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
        """Remove GIS.lab client machine from list of known machines.

        :todo: to be implemented

        :param mac: MAC address to be removed from the list
        """
        pass

    @classmethod
    def machines(cls):
        """Get list of known GIS.lab client machines.

        :return: list of MAC addresses
        """
        try:
            with open(cls.known_machines_list_file) as f:
                return f.read().splitlines()
        except IOError as e:
            raise GISLabAdminError(str(e))
    
    @classmethod
    def machine_policy(cls):
        """Get machines policy.
        
        :return: string
        """
        try:
            with open(cls.policy_file) as f:
                return f.read().rstrip('\n')
        except IOError as e:
            raise GISLabAdminError(str(e))
