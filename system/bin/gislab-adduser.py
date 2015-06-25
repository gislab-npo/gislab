#!/usr/local/python-virtualenvs/gislab-python/bin/python

"""Create GIS.lab user account.

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.
"""

import sys

from gislab.admin.utils import parse_arguments
from gislab.admin import GISLabAdmin, GISLabUser, GISLabAdminError, GISLabAdminLogger

def main():
    # parse command arguments
    opts = parse_arguments(desc='Create GIS.lab user account.',
                           positional=(('username', 'username',
                                        'user name can contain only lower case digits and numbers'),),
                           required=(('-g', 'firstname', 'first name'),
                                     ('-l', 'lastname', 'last name'),
                                     ('-m', 'email', 'email')),
                           optional=(('-p', 'password',
                                      'password (default: automatically generated)'),
                                     ('-d', 'description', 'user description'),
                                     ('-s', False, 'add user to superuser\'s group')))
    
    try:
        # check if user account already exists
        if GISLabAdmin.user_exists(opts.username):
            raise GISLabAdminError("GIS.lab user '{0}' already "
                                   "exists".format(opts.username))
    
        # add new user account
        user = GISLabAdmin.user_add(opts.username, firstname=opts.g, lastname=opts.l,
                                    email=opts.m, password=opts.p, description=opts.d,
                                    superuser=opts.s)
    except GISLabAdminError as e:
        GISLabAdminLogger.error(str(e))
        return 1
    
    GISLabAdminLogger.info("GIS.lab account '{user}' created with password "
                      "'{passwd}'".format(user=opts.username, passwd=user.password))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
