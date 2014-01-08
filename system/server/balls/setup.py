#!/usr/bin/python

import os
from distutils.core import setup

# classifiers
classifiers = [
	'Development Status :: 4 - Beta',
	"Framework :: Django",
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'License :: OSI Approved :: GNU General Public License version 2.0 (GPL-2)',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Scientific/Engineering :: GIS',
]

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
package_root_dir = 'balls'
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
setup(name='balls',
	version=".".join(map(str, __import__('balls').VERSION)),
	description='storege place for text data',
	author='Marcel Dancak',
	author_email='marcel.dancak@gista.sk',
	url='http://gista.sk/',
	long_description=file('README','rb').read(),
	package_dir={'balls': '.'},
	packages=packages,
	package_data={'balls': data_files},
	classifiers=classifiers
)
