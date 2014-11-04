#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add IP address from GIS.lab network range. Runs on Linux only.

Usage: join-gislab-network.py system/host_vars/<host-file>
"""


import sys
import yaml
import subprocess

conf = yaml.load(open(sys.argv[1], "r"))

subprocess.Popen("sudo ip addr add {0}.199/24 dev eth0".format(conf["GISLAB_NETWORK"]),
	stdout=subprocess.PIPE, shell=True).stdout.read()


# vim: set ts=4 sts=4 sw=4 noet:
