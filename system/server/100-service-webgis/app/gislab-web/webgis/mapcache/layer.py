# BSD Licensed, Copyright (c) 2006-2008 MetaCarta, Inc.

import sys
from cStringIO import StringIO
from PIL import Image, ImageEnhance


DEBUG = True

class TileNotFoundException(Exception): pass


class Tile (object):
	__slots__ = ( "layer", "x", "y", "z", "data" )

	def __init__ (self, layer, x, y, z):
		self.layer = layer
		self.x = x
		self.y = y
		self.z = z
		self.data = None

	def size (self):
		return self.layer.tile_size

	def bounds (self):
		res  = self.layer.resolutions[self.z]
		minx = self.layer.extent[0] + (res * self.x * self.layer.tile_size[0])
		miny = self.layer.extent[1] + (res * self.y * self.layer.tile_size[1])
		maxx = self.layer.extent[0] + (res * (self.x + 1) * self.layer.tile_size[0])
		maxy = self.layer.extent[1] + (res * (self.y + 1) * self.layer.tile_size[1])
		return (minx, miny, maxx, maxy)

	def extent (self):
		return ",".join(map(str, self.bounds()))

class MetaTile (Tile):
	def actual_size (self):
		meta_cols, meta_rows = self.layer.get_meta_size(self.z)
		return ( self.layer.tile_size[0] * meta_cols,
				 self.layer.tile_size[1] * meta_rows )

	def size (self):
		actual = self.actual_size()
		return ( actual[0] + self.layer.metabuffer[0] * 2, 
				 actual[1] + self.layer.metabuffer[1] * 2 )

	def bounds (self):
		tilesize   = self.actual_size()
		res		   = self.layer.resolutions[self.z]
		buffer	   = (res * self.layer.metabuffer[0], res * self.layer.metabuffer[1])
		metaWidth  = res * tilesize[0]
		meta_height = res * tilesize[1]
		minx = self.layer.extent[0] + self.x * metaWidth	- buffer[0]
		miny = self.layer.extent[1] + self.y * meta_height - buffer[1]
		maxx = minx + metaWidth  + 2 * buffer[0]
		maxy = miny + meta_height + 2 * buffer[1]
		return (minx, miny, maxx, maxy)

class Layer (object):
	__slots__ = ( "project", "publish", "name", "provider_layers", "extent",
				  "tile_size", "resolutions", "image_format", "projection",
				  "cache", "debug",
				  "extent_type", "units", "mime_type",
				  "client_expire")
	
	config_properties = [
	  {'name':'provider_layers', 'description': 'Comma seperated list of provider layers associated with this layer.'},
	  {'name':'image_format', 'description':'File image format', 'default':'png'},
	  {'name':'extent', 'description':'Bounding box of the layer', 'default':'-180,-90,180,90'},
	  {'name':'projection', 'description':'Spatial Reference System for the layer', 'default':'EPSG:4326'},
	  {'name':'client_expire', 'description':'Tiles expiration time in seconds for client browser', 'default':'None'},
	]  
	
	def __init__ (self, project, publish, name, provider_layers = None, extent = (-180, -90, 180, 90),
						projection  = "EPSG:4326",
						tile_size = 256, resolutions = None,
						image_format = "png", mime_type = None, cache = None, debug = False,
						extent_type = "loose", units = "degrees", 
						client_expire = 0, **kwargs ):
		self.project = project
		self.publish = publish
		self.name = name
		self.provider_layers = provider_layers or name

		if isinstance(extent, basestring):
			extent = map(float, extent.split(","))
		tile_size = (tile_size, tile_size)
		
		self.extent = extent
		self.tile_size = tile_size
		
		self.units = units
		
		self.projection  = projection
		
		if image_format.lower() == 'jpg': 
			image_format = 'jpeg' # MIME
		self.image_format = image_format.lower()
		self.mime_type = mime_type or self.format()
		
		self.debug = debug
		
		self.cache = cache
		self.extent_type = extent_type
		self.client_expire = client_expire
		
		if isinstance(resolutions, basestring):
			resolutions = map(float,resolutions.split(","))
		self.resolutions = resolutions


	def get_resolution (self, (minx, miny, maxx, maxy)):
		return max( float(maxx - minx) / self.tile_size[0],
					float(maxy - miny) / self.tile_size[1] )

	def get_closest_level (self, res, tile_size = [256, 256]):
		diff = sys.maxint
		z = None
		for i in range(len(self.resolutions)):
			if diff > abs( self.resolutions[i] - res ):
				diff = abs( self.resolutions[i] - res ) 
				z = i
		return z

	def get_level (self, res, tile_size = [256, 256]):
		max_diff = res / max(tile_size[0], tile_size[1])
		z = None
		for i in range(len(self.resolutions)):
			if abs( self.resolutions[i] - res ) < max_diff:
				res = self.resolutions[i]
				z = i
				break
		if z is None:
			raise TileNotFoundException("Can not find resolution index for %f. Available resolutions are: \n%s" % (res, self.resolutions))
		return z

	def get_cell (self, (minx, miny, maxx, maxy), exact = True):
		if exact and self.extent_type == "strict" and not self.contains((minx, miny)): 
			raise TileNotFoundException("Lower left corner (%f, %f) is outside layer bounds %s." 
					 % (minx, miny, self.extent))
			return None

		res = self.get_resolution((minx, miny, maxx, maxy))
		x = y = None

		if exact:
			z = self.get_level(res, self.tile_size)
		else:
			z = self.get_closest_level(res, self.tile_size)

		res = self.resolutions[z]
		x0 = (minx - self.extent[0]) / (res * self.tile_size[0])
		y0 = (miny - self.extent[1]) / (res * self.tile_size[1])
		
		x = int(round(x0))
		y = int(round(y0))
		
		tilex = ((x * res * self.tile_size[0]) + self.extent[0])
		tiley = ((y * res * self.tile_size[1]) + self.extent[1])
		if exact:
			if (abs(minx - tilex)  / res > 1):
				raise TileNotFoundException("Current x value %f is too far from tile corner x %f" % (minx, tilex))  
			
			if (abs(miny - tiley)  / res > 1):
				raise TileNotFoundException("Current y value %f is too far from tile corner y %f" % (miny, tiley))  
		
		return (x, y, z)

	def get_closest_cell (self, z, (minx, miny)):
		res = self.resolutions[z]
		maxx = minx + self.tile_size[0] * res
		maxy = miny + self.tile_size[1] * res
		return self.get_cell((minx, miny, maxx, maxy), False)

	def get_tile (self, extent):
		coord = self.get_cell(extent)
		if not coord: return None
		return Tile(self, *coord)

	def contains (self, (x, y)):
		return x >= self.extent[0] and x <= self.extent[2] \
		   and y >= self.extent[1] and y <= self.extent[3]

	def grid (self, z):
		try:
			width  = (self.extent[2] - self.extent[0]) / (self.resolutions[z] * self.tile_size[0])
			height = (self.extent[3] - self.extent[1]) / (self.resolutions[z] * self.tile_size[1])
		except IndexError:
			raise TileNotFoundException("Requested zoom level %s does not exist" % z)
		return (width, height)

	def format (self):
		return "image/" + self.image_format
	
	def render_tile (self, tile):
		# To be implemented by subclasses
		pass 

	def render (self, tile, force=False):
		return self.render_tile(tile)

class MetaLayer (Layer):
	__slots__ = ('metasize', 'metabuffer')

	def __init__ (self, project, publish, name, metasize = 5, metabuffer = 0, **kwargs):
		Layer.__init__(self, project, publish, name, **kwargs)

		self.metasize = (metasize, metasize)
		self.metabuffer = (metabuffer, metabuffer)

	def get_meta_size (self, z):
		maxcol, maxrow = self.grid(z)
		return ( min(self.metasize[0], int(maxcol + 1)), 
				 min(self.metasize[1], int(maxrow + 1)) )

	def get_meta_tile (self, tile):
		x = int(tile.x / self.metasize[0])
		y = int(tile.y / self.metasize[1])
		return MetaTile(self, x, y, tile.z) 

	def render_meta_tile (self, metatile, tile):
		data = self.render_tile(metatile)
		image = Image.open( StringIO(data) )

		meta_cols, meta_rows = self.get_meta_size(metatile.z)
		meta_height = meta_rows * self.tile_size[1] + 2 * self.metabuffer[1]
		for i in range(meta_cols):
			for j in range(meta_rows):
				minx = i * self.tile_size[0] + self.metabuffer[0]
				maxx = minx + self.tile_size[0]
				### this next calculation is because image origin is (top,left)
				maxy = meta_height - (j * self.tile_size[1] + self.metabuffer[1])
				miny = maxy - self.tile_size[1]
				subimage = image.crop((minx, miny, maxx, maxy))
				subimage.info = image.info
				buffer = StringIO()
				if image.mode != 'P' and image.info.has_key('transparency'):
					subimage.save(buffer, self.image_format, transparency=image.info['transparency'])
				else:
					subimage.save(buffer, self.image_format, quality=85)
				buffer.seek(0)
				subdata = buffer.read()
				x = metatile.x * self.metasize[0] + i
				y = metatile.y * self.metasize[1] + j
				subtile = Tile( self, x, y, metatile.z )
				self.cache.set( subtile, subdata )
				if x == tile.x and y == tile.y:
					tile.data = subdata

		return tile.data

	def render (self, tile, force=False):
		metatile = self.get_meta_tile(tile)
		try:
			self.cache.lock(metatile)
			image = None
			if not force:
				image = self.cache.get(tile)
			if not image:
				image = self.render_meta_tile(metatile, tile)
		finally:
			self.cache.unlock(metatile)
		return image
