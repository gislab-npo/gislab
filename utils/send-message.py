#!/usr/bin/env python
"""
Send message to 'gislab' IRC chat room.
Requires to run script 'utils/join-gislab-network.py' first to get connection
with server.

USAGE: send-message.py <message>
"""

import os, sys
import re
import socket

try:
    message = sys.argv[1]
except IndexError:
    print __doc__
    sys.exit(0)

DIR=os.path.dirname(os.path.abspath(__file__))

def get_config(variable):
    c = open(os.path.join(os.path.dirname(DIR), "config.cfg"), "ro")
    for line in c:
        if re.match("^" + variable, line):
            value = line.split("=")[1].replace("'", "").replace('"', '')
            c.close()
            break
    c = open(os.path.join(os.path.dirname(DIR), "config-user.cfg"), "ro")
    for line in c:
        if re.match("^" + variable, line):
            value = line.split("=")[1].replace("'", "").replace('"', '')
            c.close()
            break
    return value.strip()


GISLAB_NETWORK = get_config("GISLAB_NETWORK")
HOST="{0}.5".format(GISLAB_NETWORK)
PORT=6667
NICK=IDENT=os.environ['USER']
REALNAME="script"
CHANNEL="gislab"

s=socket.socket( socket.AF_INET, socket.SOCK_STREAM )
s.connect((HOST, PORT))
print s.recv(4096)
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN #%s\r\n" % CHANNEL)
s.send("PRIVMSG #gislab :%s\r\n" % message)
s.send("QUIT: End of message.\r\n")
s.recv(4096)
s.close()

print "Done."

# vim: ts=8 sts=4 sw=4 et:
