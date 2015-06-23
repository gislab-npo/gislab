"""GIS.lab Management Library

Utilities

(C) 2015 by the GIS.lab Development Team

This program is free software under the GNU General Public License
v3. Read the file LICENCE.md that comes with GIS.lab for details.

.. sectionauthor:: Martin Landa <landa.martin gmail.com>
"""

import os
import argparse
import ldap
import pwd
import re

import hashlib
from base64 import encodestring as encode
from base64 import decodestring as decode

from .pwgen import pwgen
from .logger import GISLabAdminLogger
from .exception import GISLabAdminError

def parse(desc, positional=(), required=(), optional=()):
    """Parse command line arguments.

    :param desc: command description
    :param positionnal: tuple of positional arguments
    :param required: tuple of required arguments
    :param optional: tuple of optional arguments

    :return: list of parsed arguments
    """
    parser = argparse.ArgumentParser(description=desc)
    for key, meta, desc in positional:
        args = {}
        if meta is None:
            args['nargs'] = '?'
        parser.add_argument(key, metavar=meta, type=str,
                            help=desc, **args)
    requiredNamed = parser.add_argument_group('required named arguments')

    for key, meta, desc in required:
        requiredNamed.add_argument(key,
                                   metavar=meta,
                                   type=str,
                                   required=True,
                                   help=desc)

    for key, meta, desc in optional:
        args = {}
        if meta and type(meta) is str:
            if meta[-1] == '?':
                args['nargs'] = '?'
                meta = meta[:-1]
                args['const'] = True
            args['metavar'] = meta
            args['type'] = str
            args['action'] = 'store'
        else:
            args['action'] = 'store_true'
            args['default'] = meta

        parser.add_argument(key,
                            help=desc, **args)

    return parser.parse_args()

def password_generate(size=8):
    """Generate random user password.

    return: password
    """
    return pwgen(size, numerals=True, no_symbols=True)

def password_encrypt(password):
    """Return SHA1 encrypted password.

    :return: encrypted password
    """
    salt = os.urandom(4)
    h = hashlib.sha1(password)
    h.update(salt)

    ret = "{SSHA}" + encode(h.digest() + salt)
    GISLabAdminLogger.debug("Encrypted password '{}': {}".format(password, ret.rstrip('\n')))
    return ret

def nextuid(min_uid=3000):
    """Get next free user ID.

    :param min_uid: starting uid

    :return: uid as integer
    """
    while min_uid:
        try:
            pwd.getpwuid(min_uid)
            min_uid+=1
        except KeyError:
            return min_uid

def read_env(filename):
    """Read variables from file.

    :param filename: absolute path to file
    """
    reg = re.compile('\s+(?P<name>\w+)(\=(?P<value>.+))*')
    with open(filename) as f:
        for line in f.readlines():
            m = reg.match(line)
            if not m:
                continue
            name = m.group('name')
            value = ''
            if m.group('value'):
                value = m.group('value').strip('"')
            os.environ[name] = value
