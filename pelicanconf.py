#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Ivan Minčík'
SITENAME = u'GIS.lab'
SITESUBTITLE = u'... rapid GIS office deployment'
SITEURL = 'http://imincik.github.io/testpelican'

TIMEZONE = 'Europe/Bratislava'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
#LINKS =  (
#	('GISTA s.r.o.', 'http://www.gista.sk'),
#	('GISTA s.r.o.', 'http://www.gista.sk'),
#)

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DISPLAY_PAGES_ON_MENU = True
DEFAULT_PAGINATION = 10

MD_EXTENSIONS = ['codehilite(css_class=highlight)', 'extra']

THEME = "themes/blueidea"
DISPLAY_CATEGORIES_ON_MENU = False
PAGES_SORT_ATTRIBUTE = 'order'
GITHUB_URL = 'https://github.com/imincik/gis-lab'

STATIC_PATHS = [
	'robots.txt',
	'images',
]

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = False
