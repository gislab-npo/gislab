#!/usr/local/python-virtualenvs/gislab-python/bin/python

"""
Modify/List GIS.lab user account(s).

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.
"""

import sys
from getpass import getpass

from gislab.admin.utils import parse_arguments
from gislab.admin import GISLabAdmin, GISLabUser, GISLabAdminError, GISLabAdminLogger

def main():
    # parse command arguments
    opts = parse(desc='Modify GIS.lab user account. Optionally list user accounts.',
                positional=(('username', None,
                             'user name (if not given than list all existing users)'),),
                optional=(('-g', 'firstname', 'first name'),
                          ('-l', 'lastname', 'last name'),
                          ('-m', 'email', 'email'),
                          ('-p', 'password?', 'password'),
                          ('-d', 'description', 'user description'),
                          ('-s', None, 'add user to superuser\'s group')))

    try:
        if opts.g or opts.l or opts.m or opts.p or opts.d or opts.s:
            if opts.p is True:
                # interactively ask for password
                opts.p = getpass()
            
            if opts.username:
                # modify selected user account
                GISLabAdmin.user_modify(opts.username, firstname=opts.g, lastname=opts.l,
                                        email=opts.m, password=opts.p,
                                        description=opts.d, superuser=opts.s)
                GISLabAdminLogger.info("GIS.lab account '{0}' updated.".format(opts.username))
            else:
                raise GISLabAdminError("GIS.lab username required")
            
        if opts.username:
            sys.stdout.write('{}\n'.format(GISLabAdmin.user_get(opts.username)))
        else:
            # no account selected, list all user accounts
            for user in GISLabAdmin.users():
                sys.stdout.write('{}\n'.format(user))
        
    except GISLabAdminError as e:
         GISLabAdminLogger.error(str(e))
         return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
