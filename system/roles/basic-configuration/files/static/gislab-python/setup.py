#!/usr/bin/env python

import os
from setuptools import setup, find_packages


# classifiers
classifiers = [
	'Development Status :: 4 - Beta',
	'Environment :: Web Environment',
	'Environment :: Console',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: GNU General Public License version 3.0 (GPLv3)',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Scientific/Engineering :: GIS',
]

# setup
setup(name='gislab-python',
	version=".".join(map(str, __import__('gislab').VERSION)),
	description='GIS.lab Python Library',
	author='Martin Landa',
	author_email='landa.martin gmail.com',
	url='https://github.com/imincik/gis-lab/',
	packages=find_packages(),
	include_package_data=True,
	classifiers=classifiers
)


# vim: set ts=4 sts=4 sw=4 noet:
