# BSD Licensed, Copyright (c) 2006-2008 MetaCarta, Inc.

from webgis.mapcache.layer import MetaLayer
from webgis.mapcache import client

class WmsLayer(MetaLayer):

	def __init__ (self, project, publish, name, provider_url, provider_image_format = None, user = None, password = None, **kwargs):
		MetaLayer.__init__(self, project, publish, name, **kwargs) 
		self.provider_url = provider_url
		self.provider_image_format = provider_image_format or self.image_format
		self.user = user
		self.password = password
		self.client = client.WMS(self.provider_url, self.user, self.password)

	def render_tile(self, tile):
		tile.data, response = self.client.fetch({
		  "BBOX": tile.extent(),
		  "WIDTH": tile.size()[0],
		  "HEIGHT": tile.size()[1],
		  "SRS": self.projection,
		  "FORMAT": self.provider_image_format,
		  "LAYERS": self.provider_layers,
		  "TRANSPARENT": True
		})
		return tile.data


# vim: set ts=4 sts=4 sw=4 noet:
