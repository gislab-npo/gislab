# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import os.path

from django.conf import settings
from django.http import HttpResponse

from webgis.mapcache.layer import Tile, TileNotFoundException
from webgis.mapcache.layers.wms import WmsLayer
from webgis.mapcache.caches.disk import Disk


def get_tile_response(layer, z=0, x=0, y=0):
	tile = Tile(layer, int(x), int(y), int(z))
	cache = Disk(base=os.path.join(settings.MEDIA_ROOT, 'cache'))
	layer.cache = cache

	image = cache.get(tile)
	if not image:
		data = layer.render(tile)
		if not data:
			raise Exception("Zero length data returned from layer.")
	layer = tile.layer
	resp = HttpResponse(tile.data, content_type=layer.format())
	#resp['Content-Length'] = len(image)
	return resp
