# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import xml.etree.ElementTree as etree


class MetadataParser(object):
	authentication = None
	_elems_prefix = ""

	def __init__(self, filename):
		self._get_metadata(filename)

	def _opt_text_elem(self, root, path, default=""):
		elem = root.find(path)
		if elem is not None:
			return elem.text
		return default

	def _get_metadata(self, filename):
		with open(filename, 'r') as f:
			root = etree.parse(f).getroot()
			authentication_elem = root.find("Authentication")
			allow_anonymous = False
			require_superuser = False
			if authentication_elem is not None:
				allow_anonymous = self._opt_text_elem(authentication_elem, 'AllowAnonymous', str(allow_anonymous)).lower() == 'true'
				require_superuser = self._opt_text_elem(authentication_elem, 'RequireSuperuser', str(require_superuser)).lower() == 'true'
			self.authentication = {
				'allow_anonymous': allow_anonymous,
				'require_superuser': require_superuser
			}
