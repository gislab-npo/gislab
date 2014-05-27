#!/usr/bin/python

import os
from distutils.core import setup

# classifiers
classifiers = [
	'Development Status :: 4 - Beta',
	"Framework :: Django",
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'License :: OSI Approved :: GNU General Public License version 3.0 (GPLv3)',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Scientific/Engineering :: GIS',
]

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
package_root_dir = 'webgis'
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
	os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(package_root_dir):
	# Ignore dirnames that start with '.'
	for i, dirname in enumerate(dirnames):
		if dirname.startswith('.'): del dirnames[i]
	if '__init__.py' in filenames:
		pkg = dirpath.replace(os.path.sep, '.')
		if os.path.altsep:
			pkg = pkg.replace(os.path.altsep, '.')
		packages.append(pkg)
	elif filenames:
		prefix = dirpath[len(package_root_dir)+1:] # Strip "package_root_dir/" from path
		for f in filenames:
			data_files.append(os.path.join(prefix, f))

# setup
setup(name='gislab-webgis',
	version=".".join(map(str, __import__('webgis').VERSION)),
	description='GIS.lab Web application',
	author='Marcel Dancak, Ivan Mincik',
	author_email='dancakm@gmail.com, ivan.mincik@gmail.com',
	url='https://github.com/imincik/gis-lab/',
	long_description=file('README.md','rb').read(),
	package_dir={'gislab-webgis': '.'},
	packages=packages,
	package_data={'webgis': data_files},
	classifiers=classifiers
)
