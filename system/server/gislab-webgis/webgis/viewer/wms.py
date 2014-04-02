# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import urllib2
import contextlib
import xml.etree.ElementTree as etree


class WmsLayer(object):
	title = None
	name = None
	properties = None
	projections = None
	extents = None
	parent = None
	sublayers = None

	def __init__(self, **kwargs):
		self.projections = []
		self.extents = {}
		for param, val in kwargs.iteritems():
			setattr(self, param, val)

	def __repr__(self):
		return self.name

	def __str__(self):
		return str(self.name)

	def __unicode__(self):
		return unicode(self.name)


class WmscLayer(object):
	title = None
	name = None
	properties = None
	projection = None
	extent = None
	resolutions = None
	image_format = None

	def __init__(self, **kwargs):
		for param, val in kwargs.iteritems():
			setattr(self, param, val)

	def __repr__(self):
		return self.name

	def __str__(self):
		return str(self.name)

	def __unicode__(self):
		return unicode(self.name)


class WmsGetCapabilitiesService(object):
	title = ""
	author = ""
	organization = ""
	abstract = ""

	featureinfo_formats = None
	wms_root_layer = None
	wms_layers = None
	wmsc_layers = None

	_elems_prefix = ""

	def __init__(self, getprojectsettings_url):
		self.featureinfo_formats = []
		self.print_composers = []
		self.wms_layers = {}
		self.wmsc_layers = {}
		self._get_capabilities(getprojectsettings_url)

	def _opt_text_elem(self, root, path, default=""):
		elem = root.find(path)
		if elem is not None:
			return elem.text
		return default

	def _parse_layer(self, layer_elem):
		_ = self._elem_with_prefix
		layer = WmsLayer(
			title = self._opt_text_elem(layer_elem, _('Title')),
			name = self._opt_text_elem(layer_elem, _('Name')),
		)
		layer.properties = layer_elem.attrib

		crs_elems = layer_elem.findall(_('CRS'))
		for crs_elem in crs_elems:
			layer.projections.append(crs_elem.text)

		# WGS84 bbox
		bbox_elem = layer_elem.find(_('EX_GeographicBoundingBox'))
		if bbox_elem is not None:
			extent = (
				float(bbox_elem.find(_('westBoundLongitude')).text),
				float(bbox_elem.find(_('southBoundLatitude')).text),
				float(bbox_elem.find(_('eastBoundLongitude')).text),
				float(bbox_elem.find(_('northBoundLatitude')).text),
			)
			layer.extents["EPSG:4326"] = extent

		bbox_elems = layer_elem.findall(_('BoundingBox'))
		for bbox_elem in bbox_elems:
			bbox = map(float, (bbox_elem.attrib['minx'], bbox_elem.attrib['miny'], bbox_elem.attrib['maxx'], bbox_elem.attrib['maxy']))
			bbox_projection = bbox_elem.attrib.get('CRS') or bbox_elem.attrib.get('SRS')
			layer.extents[bbox_projection] = bbox

		sublayers_elems = layer_elem.findall(_('Layer'))
		if sublayers_elems:
			layer.sublayers = []
			for sublayer_elem in sublayers_elems:
				sublayer = self._parse_layer(sublayer_elem)
				sublayer.parent = layer
		else:
			self.wms_layers[layer.name] = layer
		return layer

	def _parse_tileset_layer(self, tileset_elem):
		_ = self._elem_with_prefix
		layer = WmscLayer(
			name = self._opt_text_elem(tileset_elem, _('Layers')),
			resolutions = map(float, tileset_elem.find(_('Resolutions')).text.split()),
			image_format = tileset_elem.find(_('Format')).text,
			tile_width = int(tileset_elem.find(_('Width')).text),
			tile_height = int(tileset_elem.find(_('Height')).text),
		)
		layer.properties = tileset_elem.attrib

		bbox_elem = tileset_elem.find(_('BoundingBox'))
		if bbox_elem is not None:
			bbox = map(float, (bbox_elem.attrib['minx'], bbox_elem.attrib['miny'], bbox_elem.attrib['maxx'], bbox_elem.attrib['maxy']))
			layer.projection = bbox_elem.attrib.get('CRS') or bbox_elem.attrib.get('SRS')
			layer.extent = bbox
		else:
			layer.projection = "EPSG:4326"
			bbox_elem = tileset_elem.find(_('EX_GeographicBoundingBox'))
			if bbox_elem is not None:
				layer.extent = (
					float(bbox_elem.find(_('westBoundLongitude')).text),
					float(bbox_elem.find(_('southBoundLatitude')).text),
					float(bbox_elem.find(_('eastBoundLongitude')).text),
					float(bbox_elem.find(_('northBoundLatitude')).text),
				)
		return layer

	def _elem_with_prefix(self, elem_name):
		return "{0}{1}".format(self._elems_prefix, elem_name)

	def _get_capabilities(self, getprojectsettings_url):
		with contextlib.closing(urllib2.urlopen(getprojectsettings_url)) as resp:
			root = etree.parse(resp).getroot()
			if root.tag.startswith("{"):
				self._elems_prefix = root.tag[0 : root.tag.index("}")+1]
			_ = self._elem_with_prefix
			service_elem = root.find(_("Service"))
			capability_elem = root.find(_("Capability"))
			if service_elem  is None or capability_elem is None:
				raise Exception("Unexpected GetCapabilities response")

			# WMS Layers
			root_layer_elem = capability_elem.find(_("Layer"))
			if root_layer_elem is not None:
				self.wms_root_layer = self._parse_layer(root_layer_elem)
			self.wms_layers[self.wms_root_layer.name] = self.wms_root_layer

			# WMS-C Layers
			vendor_specific_elem = capability_elem.find(_("VendorSpecificCapabilities"))
			if vendor_specific_elem is not None:
				tileset_elems = vendor_specific_elem.findall(_('TileSet'))
				if tileset_elems:
					for tileset_elem in tileset_elems:
						layer = self._parse_tileset_layer(tileset_elem)
						self.wmsc_layers[layer.name] = layer
						#print "WMSC", layer.image_format
