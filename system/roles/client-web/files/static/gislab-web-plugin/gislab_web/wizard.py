# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GIS.lab Web plugin
 Publish your projects into GIS.lab Web application
 ***************************************************************************/
"""

class PublishPage(object):

	def __init__(self, plugin, page, metadata=None):
		self.plugin = plugin
		self.dialog = plugin.dialog
		self.loaded_metadata = metadata
		self.initialized = False
		page.initializePage = self._initialize_page
		page.validatePage = self.validate
		page.handler = self

	def _initialize_page(self):
		if not self.initialized:
			self.initialize(self.loaded_metadata)
			self.initialized = True
		self.show()

	def initialize(self, metadata=None):
		pass

	def show(self):
		pass

	def validate(self):
		return True

	def before_publish(self):
		pass

	def get_metadata(self):
		pass
