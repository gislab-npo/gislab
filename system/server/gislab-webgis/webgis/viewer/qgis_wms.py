# -*- coding: utf-8 -*-
"""
Author: Ivan Mincik, ivan.mincik@gmail.com
Author: Marcel Dancak, marcel.dancak@gista.sk
"""

import urllib2
import contextlib
import xml.etree.ElementTree as etree


ATTRIBUTE_TYPE = {
	'QString': 'text',
	'double': 'double',
	'qlonglong': 'integer'
}

class QgisLayer(object):
	title = None
	name = None
	properties = None
	attributes = None
	projection = None
	extent = None
	sublayers = None
	attribution = None

	def __init__(self, **kwargs):
		for param, val in kwargs.iteritems():
			setattr(self, param, val)

	def __repr__(self):
		return self.name

	def __str__(self):
		return str(self.name)

	def __unicode__(self):
		return unicode(self.name)


class QgisGetProjectSettingsService(object):
	title = ""
	author = ""
	organization = ""
	abstract = ""

	featureinfo_formats = None
	print_composers = None
	root_layer = None
	layers_order = None

	def __init__(self, getprojectsettings_url):
		self.featureinfo_formats = []
		self.print_composers = []
		self._get_project_settings(getprojectsettings_url)

	def _opt_text_elem(self, root, path, default=""):
		elem = root.find(path)
		if elem is not None:
			return elem.text
		return default

	def _parse_layer(self, layer_elem):
		layer = QgisLayer(
			title = layer_elem.find('{http://www.opengis.net/wms}Title').text,
			name = layer_elem.find('{http://www.opengis.net/wms}Name').text,
		)
		layer.properties = layer_elem.attrib

		sublayers_elems = layer_elem.findall("{http://www.opengis.net/wms}Layer")
		if sublayers_elems:
			layer.sublayers = [self._parse_layer(sublayer_elem) for sublayer_elem in sublayers_elems]

		bbox_elem = layer_elem.find("{http://www.opengis.net/wms}BoundingBox")
		if bbox_elem is not None:
			bbox = map(float, (bbox_elem.attrib['minx'], bbox_elem.attrib['miny'], bbox_elem.attrib['maxx'], bbox_elem.attrib['maxy']))
			layer.projection = bbox_elem.attrib['CRS']
			layer.extent = bbox
		else:
			layer.projection = "EPSG:4326"
			bbox_elem = layer_elem.find("{http://www.opengis.net/wms}EX_GeographicBoundingBox")
			layer.extent = (
				float(bbox_elem.find("{http://www.opengis.net/wms}westBoundLongitude").text),
				float(bbox_elem.find("{http://www.opengis.net/wms}southBoundLatitude").text),
				float(bbox_elem.find("{http://www.opengis.net/wms}eastBoundLongitude").text),
				float(bbox_elem.find("{http://www.opengis.net/wms}northBoundLatitude").text),
			)

		attributes = []
		attributes_elem = layer_elem.find('{http://www.opengis.net/wms}Attributes')
		if attributes_elem is not None:
			for attrib_elem in attributes_elem:
				attrib_type = ATTRIBUTE_TYPE.get(attrib_elem.attrib['type'])
				if attrib_type:
					attributes.append({
						'name': attrib_elem.attrib['name'],
						'type': attrib_type
					})
		layer.attributes = attributes

		attribution_elem = layer_elem.find("{http://www.opengis.net/wms}Attribution")
		if attribution_elem is not None:
			url = ''
			url_elem = attribution_elem.find('{http://www.opengis.net/wms}OnlineResource')
			if url_elem is not None:
				url = url_elem.attrib.get('{http://www.w3.org/1999/xlink}href')
			layer.attribution = {
				'title': self._opt_text_elem(attribution_elem, "{http://www.opengis.net/wms}Title"),
				'url': url
			}
		return layer

	def _get_project_settings(self, getprojectsettings_url):
		with contextlib.closing(urllib2.urlopen(getprojectsettings_url)) as resp:
			root = etree.parse(resp).getroot()
			service_elem = root.find("{http://www.opengis.net/wms}Service")
			capability_elem = root.find("{http://www.opengis.net/wms}Capability")
			if service_elem  is None or capability_elem is None:
				raise Exception("Unexpected GetProjectSettings response")

			# Project info
			self.title = self._opt_text_elem(service_elem, "{http://www.opengis.net/wms}Title")
			self.abstract = self._opt_text_elem(service_elem, "{http://www.opengis.net/wms}Abstract")
		
			contact_elem = service_elem.find("{http://www.opengis.net/wms}ContactInformation")
			if contact_elem is not None:
				self.author = self._opt_text_elem(contact_elem, ".//{http://www.opengis.net/wms}ContactPerson")
				self.organization = self._opt_text_elem(contact_elem, ".//{http://www.opengis.net/wms}ContactOrganization")
				self.email = self._opt_text_elem(contact_elem, ".//{http://www.opengis.net/wms}ContactElectronicMailAddress")

			# FeatureInfo
			getfeatureinfo_elem = capability_elem.find(".//{http://www.opengis.net/wms}GetFeatureInfo")
			if getfeatureinfo_elem is not None:
				self.featureinfo_formats = [format_elem.text for format_elem in getfeatureinfo_elem.findall("{http://www.opengis.net/wms}Format")]

			# Layers
			layers = []
			root_layer_elem = capability_elem.find("{http://www.opengis.net/wms}Layer")
			self.root_layer = self._parse_layer(root_layer_elem)

			layers_order = self._opt_text_elem(capability_elem, "{http://www.opengis.net/wms}LayerDrawingOrder")
			if layers_order:
				self.layers_order = layers_order.split(",")

			# Print Composers
			composer_templates_elem = capability_elem.find(".//{http://www.opengis.net/wms}ComposerTemplates")
			if composer_templates_elem is not None:
				print_composers = []
				for composer_template in composer_templates_elem:
					# take only map0
					composer_map = composer_template.find("{http://www.opengis.net/wms}ComposerMap[@name='map0']")
					if composer_map is not None:
						print_composer = composer_template.attrib
						maps = [composer_map.attrib]
						labels = [composer_label.attrib['name'] for composer_label in composer_template.findall("{http://www.opengis.net/wms}ComposerLabel")]

						print_composer = {
							'maps': maps,
							'labels': labels
						}
						print_composer.update(composer_template.attrib)
						print_composers.append(print_composer)
				self.print_composers = print_composers

