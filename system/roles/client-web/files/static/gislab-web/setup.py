#!/usr/bin/env python

import os
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

# setup
setup(name='gislab-web',
	version=".".join(map(str, __import__('webgis').VERSION)),
	description='GIS.lab Web application',
	author='Marcel Dancak, Ivan Mincik',
	author_email='dancakm@gmail.com, ivan.mincik@gmail.com',
	url='https://github.com/imincik/gis-lab/',
	packages=find_packages(),
	include_package_data=True,
	classifiers=classifiers
)

# vim: set ts=4 sts=4 sw=4 noet:
