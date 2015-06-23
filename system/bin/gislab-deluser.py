#!/usr/local/python-virtualenvs/gislab-python/bin/python

"""
Delete GIS.lab user account.

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.
"""

import sys

from gislab.admin.utils import parse_arguments
from gislab.admin import GISLabAdmin, GISLabUser, GISLabAdminError, GISLabAdminLogger

def main():
    # parse command arguments
    opts = parse(desc='Delete GIS.lab user account.',
                 positional=(('username', 'username', 'user name'),),
                 optional=(('-b', None,'backup user data'),
                           ('-f', None,
                            'force running this command - do not ask before '
                            'deleting account')))
    
    # delete existing user account
    try:
        GISLabAdminLogger.warning("This command will completely remove GIS.lab user "
                             "account '{}' including all data!".format(opts.username))
        if not opts.f:
            try:
                answer = raw_input("Continue ? [ENTER to continue, CTRL-C to cancel]\n")
            except (KeyboardInterrupt, EOFError) as e:
                return 0
        
        if opts.b:
            try:
                GISLabAdmin.user_backup(opts.username)
            except GISLabAdminError as e:
                GISLabAdminLogger.warning("Unable to backup user '{0}': {1}".format(opts.username, e))
        
        GISLabAdmin.user_delete(opts.username)
    except GISLabAdminError as e:
        GISLabAdminLogger.error(str(e))
        return 1
    
    GISLabAdminLogger.info("GIS.lab account '{0}' removed".format(opts.username))
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError) as e:
        sys.exit(0)
