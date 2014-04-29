# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import json


class MetadataParser(object):

	def __init__(self, filename):
		self._get_metadata(filename)

	def _get_metadata(self, filename):
		with open(filename, 'r') as f:
			self.metadata = json.load(f)

	def __getattr__(self, name):
		return self.metadata.get(name)
