"""GIS.lab Management Library

Top level administration

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.

.. sectionauthor:: Martin Landa <landa.martin gmail.com>
"""

import os
import re
import fileinput
import sys
from subprocess import call

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

	def __del__(self):
		"""Class destructor.

		Close LDAP connection.
		"""
		GISLabUser.unbind()

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
		return GISLabUser.list()

	@staticmethod
	def user_get(username):
		"""Get GIS.lab user object.

		Throw GISLabAdminError if user doesn't exists.

		:param username: user name

		:return: GISLabUser object
		"""
		return GISLabUser.get(username)

	@staticmethod
	def user_exists(username):
		"""Check if GIS.lab user exists.

		:param username: user name

		:return: True if user exists otherwise False
		"""
		return GISLabUser.exists(username)

	@staticmethod
	def user_backup(username):
		"""Backup GIS.lab user account.

		Throw GISLabAdminError if user doesn't exists.

		:param username: user name
		"""
		# GISLabUser.get(username).backup()
		raise NotImplementedError("User backup not implemented yet")

	@staticmethod
	def user_restore(username):
		"""Restore GIS.lab user account from backup.

		Throw GISLabAdminError if user already exists.

		:param username: user name

		:return: GISLabUser object
		"""
		# return GISLabUser.restore(username)
		raise NotImplementedError("User restore not implemented yet")

	@classmethod
	def machine_add(cls, mac):
		"""Add machine to list of known GIS.lab machines.
		
		:param mac: MAC address to be added
		"""
		p = re.compile('^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}$')
		if not p.match(mac):
			raise GISLabAdminError("Skipping MAC address {} - invalid format".format(mac))
		
		try:
			# check if mac address is already registered
			with open(cls.known_machines_list_file) as f:
				for line in f.read().splitlines():
					if mac == line:
						GISLabAdminLogger.info("MAC address {} already registered".format(mac))
						return
			
			# add records to known machines list file in /etc/gislab
			with open(cls.known_machines_list_file, 'a') as f:
				f.write("{}\n".format(mac))
			GISLabAdminLogger.debug("MAC address {} added to the list of known machines".format(mac))
			
		except IOError as e:
			raise GISLabAdminError("Unable to add machine: {}".format(e))
		
		# generate known machines DHCP configuration file
		cls._known_machines_dhcp_file()
		cls._restart_dhcp_server()
		GISLabAdminLogger.info("Machines added successfully")

	@classmethod
	def machine_delete(cls, mac):
		"""Remove machine from list of known GIS.lab machines.

		:param mac: MAC address
		"""
		found = False
		for line in fileinput.input(cls.known_machines_list_file, inplace=True):
			line = line.rstrip('\n')
			if mac == line:
				found = True
				continue
			sys.stdout.write("{}\n".format(line))
					
		if not found:
			GISLabAdminLogger.info("MAC address {} not found, skipped.".format(mac))
		else:
			GISLabAdminLogger.debug("MAC address {} removed from the list of known machines".format(mac))
		
		# generate known machines DHCP configuration file
		cls._known_machines_dhcp_file()
		cls._restart_dhcp_server()
		GISLabAdminLogger.info("Machines removed successfully")

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
	def machine_policy(cls, policy=None):
		"""Set/get current GIS.lab unknown machines policy.

		:param policy: set machines policy (None to get current settings)
		
		:return: current policy
		"""
		if policy and policy not in ('allow', 'deny'):
			raise GISLabAdminError("Unsupported machines policy: {0}".format(policy))
		
		try:
			if policy is None:
				with open(cls.policy_file) as f:
					policy = f.read().rstrip('\n')
			else:
				with open(cls.policy_file, 'w') as f:
					f.write('{0}\n'.format(policy))
				GISLabAdminLogger.debug("Machines policy changed to '{}'".format(policy))
		except IOError as e:
			raise GISLabAdminError(str(e))
		
		return policy

	@classmethod
	def _known_machines_dhcp_file(cls):
		"""Generate DHCP configuration file from MAC list file located
		in /etc/gislab
		"""
		try: 
			with open(cls.known_machines_dhcp_file, 'w') as f:
				f.write("group {\n") # opening bracket

				for mac in cls.machines():
					hostname = mac.replace(':', '')
					f.write("\thost {0} {{ hardware ethernet {1}; }}\n".format(hostname, mac))

			f.write("}\n") # closing bracket
		except IOError as e:
			raise GISLabAdminError(e)

	@classmethod
	def _restart_dhcp_server(cls):
		call(["service", "isc-dhcp-server", "restart"])
