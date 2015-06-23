#!/usr/local/python-virtualenvs/gislab-python/bin/python

"""
Add or remove GIS.lab client machines to/from list of known machines.

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.
"""

import sys

from gislab.admin.utils import parse_arguments
from gislab.admin import GISLabAdmin, GISLabUser, GISLabAdminError, GISLabAdminLogger

def main():
    opts = parse_arguments(desc="Add or remove GIS.lab client machines to/from list of known machines. "
                           "If 'unknown machines' policy is set to 'deny', only known machines will be authorized for connection to "
                           "GIS.lab network. If 'unknown machines' policy is set to 'allow', all machines will be authorized to connect.",
                           positional=(('mac', None,
                                        "MAC addresses must be specified in format MM:MM:MM:SS:SS:SS"),),
                           optional=(('-l', False, "print a list of known machines"),
                                     ('-a', False, "add machines to known list. If value 'all' is given instead of MAC address, "
                                      "'unknown machines' policy will be set to 'allow'"),
                                     ('-r', False, "remove machines from known list. If value 'all' is given instead of MAC address, "
                                      "'unknown machines' policy will be set to 'deny'")))
    
    try:
        # check mutually exclusive
        # TODO: do it better (argparse ???)
        nopts = 0
        nopts += 1 if opts.l else 0
        nopts += 1 if opts.a else 0
        nopts += 1 if opts.r else 0
        if nopts > 1:
            GISLabAdminLogger.error("Options -l, -a, -r are mutually exclusive")
            return 1
        if nopts == 0:
            GISLabAdminLogger.info("No option given, assuming -l") # TODO: print help instead ?
            opts.l = True
        
        if opts.l:
            # print machines
            sys.stdout.write("Policy: {}\n".format(GISLabAdmin.machine_policy()))
            sys.stdout.write("Known machines\n")
            for m in GISLabAdmin.machines():
                sys.stdout.write("  * {}\n".format(str(m)))
            return 0

        if opts.mac is None:
            GISLabAdminLogger.error("MAC required")
            return 1

        maclist = map(lambda x: x.strip(), opts.mac.split(','))
        for mac in maclist:
            try:
                if opts.a:
                    # add new machine to list
                    GISLabAdmin.machineadd(mac)
                elif opts.r:
                    # remove machine from list
                    GISLabAdmin.machinedel(mac)
            except GISLabAdminError as e:
                GISLabAdminLogger.warning(str(e))
    
    except GISLabAdminError as e:
        GISLabAdminLogger.error(str(e))
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
