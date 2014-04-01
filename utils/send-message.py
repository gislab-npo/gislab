#!/usr/bin/env python
"""Send message to 'gislab' IRC chat room.
Usage: send-message.py <message>
"""

import os, sys
import socket

try:
	message = sys.argv[1]
except IndexError:
	print __doc__
	sys.exit(0)


HOST="irc.gis.lab"
PORT=6667
NICK=IDENT="labadmin"
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

# vim: set syntax=sh ts=4 sts=4 sw=4 noet:
