#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages


# classifiers
classifiers = [
	'Development Status :: 4 - Beta',
	'Environment :: Web Environment',
	'Framework :: Django',
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'License :: OSI Approved :: GNU General Public License version 3.0 (GPLv3)',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Scientific/Engineering :: GIS',
]

exclude_from_packages = [
	'webgis.conf.project_template',
]

# version
try:
	with open('/etc/gislab_version') as f:
		for line in f:
			if re.match('^GISLAB_VERSION=', line):
				version = line.split('=')[1].replace('"', '').replace("'", "")
except IOError:
	version='unknown'

# requirements
with open("requirements.txt") as f:
	requirements = f.read().splitlines()

# setup
setup(name='gislab-web',
	version=version,
	description='GIS.lab Web client',
	author='Marcel Dancak, Ivan Mincik',
	author_email='dancakm@gmail.com, ivan.mincik@gmail.com',
	url='https://github.com/imincik/gis-lab/',
	packages=find_packages(),
	include_package_data=True,
	classifiers=classifiers,
	install_requires=requirements
)

# vim: set ts=4 sts=4 sw=4 noet:
