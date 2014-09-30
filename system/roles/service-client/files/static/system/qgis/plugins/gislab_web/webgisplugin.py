# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GIS.lab Web plugin
 Publish your projects into GIS.lab Web application
 ***************************************************************************/
"""

import os
import re
import json
import time
import datetime
import subprocess
from decimal import Decimal
from urllib import urlencode
from urlparse import parse_qs

# Import the PyQt and QGIS libraries
import PyQt4.uic
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtXml import QDomDocument

# Initialize Qt resources from file resources.py
import resources_rc
from topics import setup_topics_ui, get_topics, load_topics_from_metadata


GISLAB_VERSION_FILE = "/etc/gislab_version"
MSG_ERROR = "Error"
MSG_WARNING = "Warning"


CSS_STYLE = u"""<style type="text/css">
	body {
		background-color: #DDDDDD;
	}
	h3 {
		margin-bottom: 4px;
		margin-top: 6px;
		text-decoration: underline;
	}
	h4 {
		margin-bottom: 1px;
		margin-top: 2px;
	}
	div {
		margin-left: 10px;
	}
	ul {
		margin-top: 0px;
	}
	label {
		font-weight: bold;
	}
</style>"""

class Node(object):
	"""Tree node element for holding information about layers organization and easier manipulation."""
	name = None
	layer = None
	parent = None
	children = None
	isBaseLayerNode = False

	def __init__(self, name, children=None, layer=None):
		self.name = name
		self.layer = layer
		self.children = []
		if children:
			self.append(*children)

	def append(self, *nodes):
		for node in nodes:
			if node is not None:
				if not isinstance(node, Node):
					node = Node(node)
				node.parent = self
				self.children.append(node)

	def find(self, name):
		if name == self.name:
			return self
		for child in self.children:
			res = child.find(name)
			if res:
				return res

	def cascade(self, fn):
		for child in self.children:
			child.cascade(fn)
		fn(self)

def to_decimal_array(value):
	"""Converts list of float/string numbers or comma-separated string to list of Decimal values"""
	if isinstance(value, basestring):
		return [Decimal(res_string.strip())for res_string in value.split(',')]
	else:
		return [Decimal(res) for res in value]

def get_tile_resolutions(scales, units, dpi=96):
	"""Helper function to compute tile resolutions from map scales."""

	dpi = Decimal(dpi)
	factor = {
		'feet': Decimal('12.0'), 'meters': Decimal('39.37'),
		'miles': Decimal('63360.0'), 'degrees': Decimal('4374754.0')
	}
	return [int(scale)/(dpi*factor[units]) for scale in scales]

def get_scales_from_resolutions(resolutions, units, dpi=96):
	"""Helper function to compute map scales from tile resolutions."""
	dpi = Decimal(dpi)
	factor = {
		'feet': Decimal('12.0'), 'meters': Decimal('39.37'),
		'miles': Decimal('63360.0'), 'degrees': Decimal('4374754.0')
	}
	return [int(round(resolution * dpi * factor[units])) for resolution in resolutions]


GISLAB_WEB_URL = 'https://web.gis.lab'

DEFAULT_PROJECT_SCALES = (10000000,5000000,2500000,1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500)

osm_resolutions = to_decimal_array("""156543.03390625,78271.516953125,39135.7584765625,19567.87923828125,9783.939619140625,
4891.9698095703125,2445.9849047851562,1222.9924523925781,611.4962261962891,305.74811309814453,152.87405654907226,76.43702827453613,
38.218514137268066,19.109257068634033,9.554628534317017,4.777314267158508,2.388657133579254,1.194328566789627,0.5971642833948135""")
OSM_LAYER = {
	'name': 'OSM', 'type': 'OSM', 'title': 'Open Street Map',
	'resolutions': osm_resolutions,
	'extent': [-16319611.284727, -5615981.3413867, 16319611.284727, 5615981.3413867]
}

google_resolutions = to_decimal_array("""156543.03390625,78271.516953125,39135.7584765625,19567.87923828125,
9783.939619140625,4891.9698095703125,2445.9849047851562,1222.9924523925781,611.4962261962891,305.74811309814453,
152.87405654907226,76.43702827453613,38.218514137268066,19.109257068634033,9.554628534317017,4.777314267158508""")
google_extent = [-16319611.284727, -5615981.3413867, 16319611.284727, 5615981.3413867]
GOOGLE_LAYERS = (
	{'name': 'GROADMAP', 'type': 'google', 'title': 'Google Roadmap', 'resolutions': google_resolutions, 'extent': google_extent},
	{'name': 'GHYBRID', 'type': 'google', 'title': 'Google Hybrid', 'resolutions': google_resolutions, 'extent': google_extent},
	{'name': 'GSATELLITE', 'type': 'google', 'title': 'Google Satellite', 'resolutions': google_resolutions, 'extent': google_extent},
	{'name': 'GTERRAIN', 'type': 'google', 'title': 'Google Terrain', 'resolutions': google_resolutions, 'extent': google_extent},
)


AUTHENTICATION_OPTIONS = ('all', 'authenticated', 'owner')

class WebGisPlugin:

	dialog = None
	project = None
	run_in_gislab = False

	def __init__(self, iface):
		# Save reference to the QGIS interface
		self.iface = iface
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
		locale = QSettings().value("locale/userLocale")[0:2]
		localePath = os.path.join(self.plugin_dir, 'i18n', 'webgisplugin_{}.qm'.format(locale))

		if os.path.exists(localePath):
			self.translator = QTranslator()
			self.translator.load(localePath)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)
		self.run_in_gislab = os.path.exists(GISLAB_VERSION_FILE)

	def initGui(self):
		# Create action that will start plugin configuration
		self.action = QAction(
			QIcon(":/plugins/webgisplugin/icon.png"),
			u"Publish in GIS.lab Web", self.iface.mainWindow())
		# connect the action to the run method
		self.action.triggered.connect(self.run)

		# Add toolbar button and menu item
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToWebMenu(u"&GIS.lab Web", self.action)

	def unload(self):
		# Remove the plugin menu item and icon
		self.iface.removePluginMenu(u"&GIS.lab Web", self.action)
		self.iface.removeToolBarIcon(self.action)

	def _show_messages(self, messages):
		"""Display messages in dialog window."""
		dialog = self.dialog
		table = dialog.info_table
		if messages:
			dialog.errors_group.setVisible(True)
			rowCount = len(messages)
			table.setRowCount(rowCount)
			red = QColor.fromRgb(255, 0, 0)
			orange = QColor("#FF7F2A")
			for row_index, message in enumerate(messages):
				msg_type, msg_text = message
				item = QTableWidgetItem(msg_type)
				item.setForeground(red if msg_type == MSG_ERROR else orange)
				dialog.info_table.setItem(row_index, 0, item)
				dialog.info_table.setItem(row_index, 1, QTableWidgetItem(msg_text))
		else:
			dialog.errors_group.setVisible(False)

	def _check_publish_constrains(self):
		"""Checks whether all conditions for publishing project is satisfied,
		generating all warnings/errors displayed to user."""
		messages = []
		if self.project.isDirty():
			messages.append((MSG_ERROR, u"Project has been modified. Save it (Project > Save)."))

		map_canvas = self.iface.mapCanvas()
		if map_canvas.mapRenderer().destinationCrs().authid().startswith('USER:'):
			messages.append((
				MSG_ERROR,
				u"Project use custom coordinate system"
			))

		all_layers = [layer.name() for layer in self.iface.legendInterface().layers()]
		if len(all_layers) != len(set(all_layers)):
			messages.append((MSG_ERROR, u"Project contains layers with the same names."))

		crs_transformation, ok = self.project.readEntry("SpatialRefSys", "/ProjectionsEnabled")
		if not ok or not crs_transformation:
			messages.append((
				MSG_ERROR,
				u"'On the fly' CRS transformation not enabled ('Project > Project Properties > CRS')."
			))

		min_resolution = self.dialog.min_scale.itemData(self.dialog.min_scale.currentIndex())
		max_resolution = self.dialog.max_scale.itemData(self.dialog.max_scale.currentIndex())
		def publish_resolutions(resolutions, min_resolution=min_resolution, max_resolution=max_resolution):
			return filter(lambda res: res >= min_resolution and res <= max_resolution, resolutions)

		base_layers = [layer for layer in self.iface.legendInterface().layers() if self._is_base_layer_for_publish(layer)]
		for layer in base_layers:
			if layer.crs().authid().startswith('USER:'):
				messages.append((
					MSG_ERROR,
					u"Base layer '{0}' use custom coordinate system".format(layer.name())
				))
			resolutions = self._wmsc_layer_resolutions(layer, self._map_units())
			if resolutions is not None and not publish_resolutions(resolutions):
				messages.append((
					MSG_WARNING,
					u"Base layer '{0}' will not be visible in published project scales".format(layer.name())
				))

		overlay_layers = [layer for layer in self.iface.legendInterface().layers() if self._is_overlay_layer_for_publish(layer)]
		for layer in overlay_layers:
			layer_widget = self.dialog.overlaysTree.findItems(layer.name(), Qt.MatchExactly | Qt.MatchRecursive)
			if layer_widget:
				layer_widget = layer_widget[0]
				if layer_widget.checkState(0) == Qt.Checked:
					if layer.crs().authid().startswith('USER:'):
						messages.append((
							MSG_ERROR,
							u"Overlay layer '{0}' use custom coordinate system".format(layer.name())
						))

		self._show_messages(messages)
		for msg_type, msg_text in messages:
			if msg_type == MSG_ERROR:
				return False
		return True

	def _is_overlay_layer_for_publish(self, layer):
		"""Checks whether layer could be published as overlay layer."""
		return (layer.type() == QgsMapLayer.VectorLayer or
			(layer.type() == QgsMapLayer.RasterLayer and layer.providerType() != "wms"))

	def _is_base_layer_for_publish(self, layer):
		"""Checks whether layer could be published as base layer."""
		return layer.type() == QgsMapLayer.RasterLayer and layer.providerType() == "wms"

	def _filter_layer_visible_resolutions(self, resolutions, layer, units):
		"""Filters given tile resolutions by layer's visibility settings."""
		if layer.hasScaleBasedVisibility():
			max_scale_exclusive = layer.maximumScale()
			min_scale_inclusive = layer.minimumScale()
			max_res_exclusive, min_res_inclusive = get_tile_resolutions([max_scale_exclusive, min_scale_inclusive], units)
			return filter(lambda res: res >= min_res_inclusive and res < max_res_exclusive, resolutions)
		return resolutions

	def _wmsc_layer_resolutions(self, layer, units):
		"""Returns visible resolutions of given WMSC layer."""
		layer_resolutions = layer.dataProvider().property('resolutions')
		if layer_resolutions:
			layer_resolutions = to_decimal_array(layer_resolutions)
			if layer.hasScaleBasedVisibility():
				layer_resolutions = self._filter_layer_visible_resolutions(layer_resolutions, layer, units)
			if layer_resolutions:
				return sorted(layer_resolutions, reverse=True)
			return []
		return None

	def _map_units(self):
		"""Returns current map units name ('meters', 'feet', 'degrees', 'miles' or 'unknown')."""
		map_canvas = self.iface.mapCanvas()
		return {0: 'meters', 1: 'feet', 2: 'degrees', 3: 'unknown', 7: 'miles'}[map_canvas.mapUnits()]

	def _project_layers_resolutions(self):
		"""Calculate project resolutions as an union of resolutions calculated
		from project scales and resolutions of all WMSC layers."""
		project_tile_resolutions = set()
		units = self._map_units()

		# collect set of all resolutions from WMSC base layers
		base_layers = {layer.id(): layer for layer in self.iface.legendInterface().layers() if self._is_base_layer_for_publish(layer)}
		for layer in base_layers.itervalues():
			layer_resolutions = self._wmsc_layer_resolutions(layer, units)
			if layer_resolutions:
				project_tile_resolutions.update(layer_resolutions)

		wmsc_layers_scales = get_scales_from_resolutions(project_tile_resolutions, self._map_units())
		scales, ok = self.project.readListEntry("Scales", "/ScalesList")
		if ok and scales:
			scales = [int(scale.split(":")[-1]) for scale in scales]
			# filter duplicit scales
			scales = filter(lambda scale: scale not in wmsc_layers_scales, scales)
			project_tile_resolutions.update(get_tile_resolutions(sorted(scales, reverse=True), units))

		project_tile_resolutions = sorted(project_tile_resolutions, reverse=True)
		return project_tile_resolutions

	def _get_project_layers(self):
		"""Returns root layer node of all base layers and overlay layers."""
		legend_iface = self.iface.legendInterface()

		# ALL LAYERS TREE
		layers_reletionship = legend_iface.groupLayerRelationship()
		layers_root = Node('')
		for parent_name, child_names in layers_reletionship:
			parent = layers_root.find(parent_name)
			if not parent:
				parent = Node(parent_name)
				layers_root.append(parent)
			parent.append(*child_names)

		# filter to base layers only
		base_layers = {layer.id(): layer for layer in legend_iface.layers() if self._is_base_layer_for_publish(layer)}

		# BASE LAYERS
		def base_tree(node):
			base_children = []
			for child in node.children:
				base_child = base_tree(child)
				if base_child:
					base_children.append(base_child)
			if base_children:
				return Node(node.name, base_children)
			elif not node.children and node.name in base_layers:
				return Node(node.name, layer=base_layers[node.name])
		base_layers_tree = base_tree(layers_root)

		# OVERLAY LAYERS
		# filter to overlay layers only
		overlay_layers = {layer.id(): layer for layer in legend_iface.layers() if self._is_overlay_layer_for_publish(layer)}
		def overlays_tree(node):
			overlay_children = []
			for child in node.children:
				overlay_child = overlays_tree(child)
				if overlay_child:
					overlay_children.append(overlay_child)
			if overlay_children:
				return Node(node.name, overlay_children)
			elif not node.children and node.name in overlay_layers:
				return Node(node.name, layer=overlay_layers[node.name])
		overlay_layers_tree = overlays_tree(layers_root)

		return base_layers_tree, overlay_layers_tree


	def publish_project(self):
		"""Creates project metadata file."""
		if not self.metadata:
			return

		# create metadata file
		metadata_filename = os.path.splitext(self.project.fileName())[0] + '.meta'
		with open(metadata_filename, "w") as f:
			def decimal_default(obj):
				if isinstance(obj, Decimal):
					return float(obj)
				raise TypeError
			json.dump(self.metadata, f, indent=2, default=decimal_default)

		self.generate_confirmation_page()
		return True

	def generate_project_metadata(self):
		"""Generated project's metadata (dictionary)."""
		dialog = self.dialog
		map_canvas = self.iface.mapCanvas()
		legend_iface = self.iface.legendInterface()
		units = self._map_units()

		project_keyword_list = self.project.readListEntry("WMSKeywordList", "/")[0]
		metadata = {
			'title': self.project.readEntry("WMSServiceTitle", "/")[0] or self.project.title(),
			'abstract': self.project.readEntry("WMSServiceAbstract", "/")[0],
			'contact_person': self.project.readEntry("WMSContactPerson", "/")[0],
			'contact_organization': self.project.readEntry("WMSContactOrganization", "/")[0],
			'contact_mail': self.project.readEntry("WMSContactMail", "/")[0],
			'contact_phone': self.project.readEntry("WMSContactPhone", "/")[0],
			'online_resource': self.project.readEntry("WMSOnlineResource", "/")[0],
			'fees': self.project.readEntry("WMSFees", "/")[0],
			'access_constrains': self.project.readEntry("WMSAccessConstraints", "/")[0],
			'keyword_list':project_keyword_list if project_keyword_list != [u''] else [],
			'authentication': AUTHENTICATION_OPTIONS[dialog.authentication.currentIndex()],
			'use_mapcache': dialog.use_mapcache.isChecked(),
			'publish_date_unix': int(time.time()),
			'publish_date': time.ctime(),
		}
		if self.dialog.enable_expiration.isChecked():
			metadata['expiration'] = self.dialog.expiration.date().toString("dd.MM.yyyy")
		renderer_context = map_canvas.mapRenderer().rendererContext()
		selection_color = renderer_context.selectionColor()
		canvas_color = map_canvas.canvasColor()

		#if dialog.extent_layer.currentIndex() == 0:
		#	project_extent = map_canvas.fullExtent()
		#else:
		#	extent_layer = dialog.extent_layer.itemData(dialog.extent_layer.currentIndex())
		#	project_extent = map_canvas.mapRenderer().layerExtentToOutputExtent(extent_layer, extent_layer.extent())
		#project_extent = project_extent.toRectF().getCoords()
		project_extent = dialog.extent_layer.itemData(dialog.extent_layer.currentIndex())
		extent_buffer = dialog.extent_buffer.value()
		if extent_buffer != 0:
			project_extent = [
				project_extent[0]-extent_buffer,
				project_extent[1]-extent_buffer,
				project_extent[2]+extent_buffer,
				project_extent[3]+extent_buffer
			]
		metadata.update({
			'extent': project_extent,
			'extent_buffer': extent_buffer,
			'zoom_extent': [round(coord, 3) for coord in self.iface.mapCanvas().extent().toRectF().getCoords()],
			'projection': {
				'code': map_canvas.mapRenderer().destinationCrs().authid(),
				'is_geographic': map_canvas.mapRenderer().destinationCrs().geographicFlag()
			},
			'units': units,
			'selection_color': '{0}{1:02x}'.format(selection_color.name(), selection_color.alpha()),
			'canvas_color': '{0}{1:02x}'.format(canvas_color.name(), canvas_color.alpha()),
			'measure_ellipsoid': self.project.readEntry("Measure", "/Ellipsoid", "")[0],
			'position_precision': {
				'automatic': self.project.readBoolEntry("PositionPrecision", "/Automatic")[0],
				'decimal_places': self.project.readNumEntry("PositionPrecision", "/DecimalPlaces")[0]
			}
		})

		special_base_layers = []
		if dialog.blank.isChecked():
			special_base_layers.append({'title': 'Blank', 'name': 'BLANK', 'type': 'BLANK'})
		if metadata['projection']['code'].upper() == 'EPSG:3857':
			if dialog.osm.isChecked():
				special_base_layers.append(dict(OSM_LAYER))
			if dialog.google.currentIndex() > 0:
				special_base_layers.append(dict(GOOGLE_LAYERS[dialog.google.currentIndex()-1]))

		min_resolution = self.dialog.min_scale.itemData(self.dialog.min_scale.currentIndex())
		max_resolution = self.dialog.max_scale.itemData(self.dialog.max_scale.currentIndex())
		def publish_resolutions(resolutions, min_resolution=min_resolution, max_resolution=max_resolution):
			return filter(lambda res: res >= min_resolution and res <= max_resolution, resolutions)

		project_tile_resolutions = set(self._project_layers_resolutions())
		# collect set of all resolutions from special base layers and WMSC base layers
		for special_base_layer in special_base_layers:
			resolutions = special_base_layer.get('resolutions')
			if resolutions:
				project_tile_resolutions.update(resolutions)

		if not project_tile_resolutions:
			project_tile_resolutions = get_tile_resolutions(DEFAULT_PROJECT_SCALES, units)

		project_tile_resolutions = set(publish_resolutions(project_tile_resolutions))
		project_tile_resolutions = sorted(project_tile_resolutions, reverse=True)
		metadata['tile_resolutions'] = project_tile_resolutions

		# create base layers metadata
		default_baselayer = self.dialog.default_baselayer.itemData(self.dialog.default_baselayer.currentIndex())
		def base_layers_data(node):
			if node.children:
				sublayers_data = []
				for child in node.children:
					sublayer_data = base_layers_data(child)
					if sublayer_data:
						sublayers_data.append(sublayer_data)
				if sublayers_data:
					return {
						'name': node.name,
						'layers': sublayers_data
					}
			else:
				layer = node.layer
				source_params = parse_qs(layer.source())
				layer_data = {
					'name': layer.name(),
					'provider_type': layer.providerType(),
					'visible': layer.name() == default_baselayer,
					'extent': map_canvas.mapRenderer().layerExtentToOutputExtent(layer, layer.extent()).toRectF().getCoords(),
					'wms_layers': source_params['layers'][0].split(','),
					'projection': source_params['crs'][0],
					'format': source_params['format'][0],
					'url': source_params['url'][0],
					'dpi': layer.dataProvider().dpi(),
					'metadata': {
						'title': layer.title(),
						'abstract': layer.abstract(),
						'keyword_list': layer.keywordList()
					}
				}
				if layer.attribution():
					layer_data['attribution'] = {
						'title': layer.attribution(),
						'url': layer.attributionUrl()
					}
				layer_resolutions = layer.dataProvider().property('resolutions')
				if layer_resolutions:
					layer_resolutions = publish_resolutions(self._wmsc_layer_resolutions(layer, units))
					if not layer_resolutions:
						return None
					min_resolution = layer_resolutions[-1]
					max_resolution = layer_resolutions[0]
					upper_resolutions = filter(lambda res: res > max_resolution, project_tile_resolutions)
					lower_resolutions = filter(lambda res: res < min_resolution, project_tile_resolutions)
					layer_data.update({
						'type': 'WMSC',
						'min_resolution': min_resolution,
						'max_resolution': max_resolution,
						'resolutions': upper_resolutions + layer_resolutions + lower_resolutions,
						'tile_size': [layer.dataProvider().property('tileWidth') or 256, layer.dataProvider().property('tileHeight') or 256]
					})
				else:
					layer_data.update({
						'type': 'WMS',
						'resolutions': project_tile_resolutions
					})
					if layer.hasScaleBasedVisibility():
						layer_visible_resolutions = self._filter_layer_visible_resolutions(layer_data['resolutions'], layer, units)
						if layer_visible_resolutions:
							layer_data.update({
								'min_resolution': layer_visible_resolutions[-1],
								'max_resolution': layer_visible_resolutions[0],
							})
				return layer_data

		if self.base_layers_tree:
			base_layers_metadata = base_layers_data(self.base_layers_tree)
		else:
			base_layers_metadata = {'layers': []}

		# insert special base layers metadata
		for special_base_layer in reversed(special_base_layers):
			special_base_layer['visible'] = special_base_layer['name'] == default_baselayer
			if 'resolutions' not in special_base_layer:
				special_base_layer['resolutions'] = project_tile_resolutions
			else:
				layer_resolutions = special_base_layer['resolutions']
				visible_resolutions = publish_resolutions(special_base_layer['resolutions'])
				special_base_layer['resolutions'] = visible_resolutions
				special_base_layer['min_zoom_level'] = layer_resolutions.index(visible_resolutions[0])
				special_base_layer['max_zoom_level'] = layer_resolutions.index(visible_resolutions[-1])

			if 'extent' not in special_base_layer:
				special_base_layer['extent'] = metadata['extent']
			base_layers_metadata['layers'].insert(0, special_base_layer)

		metadata['base_layers'] = base_layers_metadata.get('layers')

		non_identifiable_layers = self.project.readListEntry("Identify", "/disabledLayers")[0] or []

		overlays_order = [layer.id() for layer in legend_iface.layers() if self._is_overlay_layer_for_publish(layer)]
		def create_overlays_data(node):
			sublayers = []
			for child in node.children:
				sublayer = create_overlays_data(child)
				if sublayer:
					sublayers.append(sublayer)
			if sublayers:
				return {
					'name': node.name,
					'layers': sublayers
				}
			elif node.layer:
				layer = node.layer
				layer_widget = dialog.overlaysTree.findItems(layer.name(), Qt.MatchExactly | Qt.MatchRecursive)[0]
				if layer_widget.checkState(0) == Qt.Unchecked:
					return None

				layer_data = {
					'name': layer.name(),
					'provider_type': layer.providerType(),
					'extent': map_canvas.mapRenderer().layerExtentToOutputExtent(layer, layer.extent()).toRectF().getCoords(),
					'projection': layer.crs().authid(),
					'visible': legend_iface.isLayerVisible(layer),
					'queryable': layer.id() not in non_identifiable_layers,
					'hidden': layer_widget.checkState(1) == Qt.Checked,
					'export_to_drawings': layer_widget.checkState(2) == Qt.Checked,
					'drawing_order': overlays_order.index(layer.id()),
					'metadata': {
						'title': layer.title(),
						'abstract': layer.abstract(),
						'keyword_list': layer.keywordList()
					}
				}
				if layer.attribution():
					layer_data['attribution'] = {
						'title': layer.attribution(),
						'url': layer.attributionUrl()
					}
				if layer.hasScaleBasedVisibility():
					layer_data['visibility_scale_min'] = layer.minimumScale()
					layer_data['visibility_scale_max'] = layer.maximumScale()

				if layer.type() == QgsMapLayer.VectorLayer:
					layer_data['type'] = 'vector'
					layer_label_settings = QgsPalLayerSettings()
					layer_label_settings.readFromLayer(layer)
					layer_data['labels'] = layer_label_settings.enabled
					if layer.hasGeometryType():
						layer_data['geom_type'] = ('POINT', 'LINE', 'POLYGON')[layer.geometryType()]

					fields = layer.pendingFields()
					attributes_data = []
					attributes_indexes = []
					for elem in layer.attributeEditorElements():
						attribs_group = elem.toDomElement(QDomDocument())
						attribs_elems = attribs_group.elementsByTagName('attributeEditorField')
						for i in range(attribs_elems.count()):
							attrib_elem = attribs_elems.item(i)
							index = int(attrib_elem.attributes().namedItem('index').nodeValue())
							name = attrib_elem.attributes().namedItem('name').nodeValue()
							attributes_indexes.append(index)
					if not attributes_indexes:
						attributes_indexes = range(fields.count())
					excluded_attributes = layer.excludeAttributesWMS()
					for index in attributes_indexes:
						field = fields.field(index)
						if field.name() in excluded_attributes:
							continue
						attribute_data = {
							'name': field.name(),
							'type': field.typeName(),
							#'length': field.length(),
							#'precision': field.precision()
						}
						if field.comment():
							attribute_data['comment'] = field.comment()
						alias = layer.attributeAlias(index)
						if alias:
							attribute_data['alias'] = alias
						attributes_data.append(attribute_data)
					layer_data['attributes'] = attributes_data
					layer_data['pk_attributes'] = [fields[index].name() for index in layer.dataProvider().pkAttributeIndexes()]
				else:
					layer_data['type'] = 'raster'
				return layer_data
		if self.overlay_layers_tree:
			metadata['overlays'] = create_overlays_data(self.overlay_layers_tree).get('layers')
		else:
			metadata['overlays'] = []

		composer_templates = []
		for composer in self.iface.activeComposers():
			composition = composer.composition()
			map_composer = composition.getComposerMapById(0)
			map_rect = map_composer.rect()
			composer_templates.append({
				# cannot get composer name other way
				'name': composer.composerWindow().windowTitle(),
				'width': composition.paperWidth(),
				'height': composition.paperHeight(),
				'map': {
					'name': 'map0',
					'width': map_rect.width(),
					'height': map_rect.height()
				},
				'labels': [item.id() for item in composition.items() if isinstance(item, QgsComposerLabel) and item.id()]
			})
		metadata['composer_templates'] = composer_templates

		message_text = dialog.message_text.toPlainText()
		if message_text:
			metadata['message'] = {
				'text': message_text,
				'valid_until': dialog.message_valid_until.date().toString("dd.MM.yyyy")
			}

		gislab_version_data = {}
		try:
			with open(GISLAB_VERSION_FILE) as f:
				param_pattern = re.compile('\s*(\w+)\s*\=\s*"([^"]*)"')
				for line in f:
					match = param_pattern.match(line)
					if match:
						name, value = match.groups()
						gislab_version_data[name] = value
		except IOError:
			pass
		metadata['gislab_unique_id'] = gislab_version_data.get('GISLAB_UNIQUE_ID', 'unknown')
		metadata['gislab_version'] = gislab_version_data.get('GISLAB_VERSION', 'unknown')
		metadata['gislab_user'] = os.environ['USER']
		return metadata

	def validate_config_page(self):
		if not self._check_publish_constrains():
			return False

		if not self.topics_initialized:
			setup_topics_ui(self.dialog, self.overlay_layers_tree)
			if self.current_metadata is not None:
				load_topics_from_metadata(self.dialog, self.current_metadata)
			self.topics_initialized = True
		return True

	def validate_topics_page(self):
		self.metadata = None
		self.metadata = self.generate_project_metadata()
		self.generate_config_summary()
		self.metadata['topics'] = get_topics(self.dialog)
		return True

	def generate_config_summary(self):
		"""Creates configuration summary of published project."""
		def format_template_data(data):
			iterator = data.iteritems() if type(data) == dict else enumerate(data)
			for key, value in iterator:
				if type(value) in (list, tuple):
					if value and isinstance(value[0], Decimal):
						value = [u'{0:.5f}'.format(v) for v in value]
					data[key] = u', '.join(map(unicode, value))
			return data

		metadata = self.metadata
		message = metadata.get('message')
		data = {
			'DEFAULT_BASE_LAYER': self.dialog.default_baselayer.currentText(),
			'SCALES': get_scales_from_resolutions(metadata['tile_resolutions'], self._map_units()),
			'PROJECTION': metadata['projection']['code'],
			'AUTHENTICATION': self.dialog.authentication.currentText(),
			'MESSAGE_TEXT': message['text'] if message else '',
			'MESSAGE_VALIDITY': message['valid_until'] if message else '',
			'EXPIRATION': metadata.get('expiration', ''),
		}

		for param in ('gislab_user', 'gislab_unique_id', 'gislab_version', 'title', 'abstract',
					'contact_person', 'contact_mail', 'contact_organization', 'extent',
					'tile_resolutions', 'units', 'measure_ellipsoid', 'use_mapcache'):
			data[param.upper()] = metadata[param]

		base_layers_summary = []
		def collect_base_layer_summary(layer_data):
			sublayers = layer_data.get('layers')
			if sublayers:
				base_layers_summary.append(u'<h4>{0}</h4><div class="subcategory">'.format(layer_data['name']))
				for sublayer_data in sublayers:
					collect_base_layer_summary(sublayer_data)
			else:
				resolutions = layer_data['resolutions']
				if 'min_resolution' in layer_data:
					resolutions = filter(lambda res: res >= layer_data['min_resolution'] and res <= layer_data['max_resolution'], resolutions)
				scales = get_scales_from_resolutions(resolutions, self._map_units())
				if 'metadata' in layer_data:
					if 'visibility_scale_max' in layer_data:
						scale_visibility = 'Maximum (inclusive): {0}, Minimum (exclusive): {1}'.format(layer_data['visibility_scale_max'], layer_data['visibility_scale_min'])
					else:
						scale_visibility = ''
					template_data = format_template_data([
						layer_data['name'],
						layer_data['extent'],
						layer_data['projection'],
						scale_visibility,
						scales,
						resolutions,
						layer_data.get('provider_type', ''),
						layer_data['attribution']['title'] if 'attribution' in layer_data and 'title' in layer_data['attribution'] else '',
						layer_data['attribution']['url'] if 'attribution' in layer_data and 'url' in layer_data['attribution'] else '',
						layer_data['metadata']['title'],
						layer_data['metadata']['abstract'],
						layer_data['metadata']['keyword_list'],
					])
					layer_summary = u"""<h4>{0}</h4>
						<ul>
							<li><label>Extent:</label> {1}</li>
							<li><label>CRS:</label> {2}</li>
							<li><label>Scale based visibility:</label> {3}</li>
							<li><label>Visible scales:</label> {4}</li>
							<li><label>Visible resolutions:</label> {5}</li>
							<li><label>Provider type:</label> {6}</li>
							<li><label>Attribution:</label>
								<ul>
									<li><label>Title:</label> {7}</li>
									<li><label>URL:</label> {8}</li>
								</ul>
							</li>
							<li><label>Metadata:</label>
								<ul>
									<li><label>Title:</label> {9}</li>
									<li><label>Abstract:</label> {10}</li>
									<li><label>Keyword list:</label> {11}</li>
								</ul>
							</li>
						</ul>""".format(*template_data)
				# Special base layers
				else:
					template_data = format_template_data([
						layer_data['name'],
						layer_data['extent'],
						scales,
						resolutions,
					])
					layer_summary = u"""<h4>{0}</h4>
						<ul>
							<li><label>Extent:</label> {1}</li>
							<li><label>Visible scales:</label> {2}</li>
							<li><label>Visible resolutions:</label> {3}</li>
						</ul>""".format(*template_data)
				base_layers_summary.append(layer_summary)

		for layer_data in metadata['base_layers']:
			collect_base_layer_summary(layer_data)
		data['BASE_LAYERS'] = '\n'.join(base_layers_summary)

		overlays_summary = []
		def collect_overlays_summary(layer_data):
			sublayers = layer_data.get('layers')
			if sublayers:
				overlays_summary.append(u'<h4>{0}</h4><div class="subcategory">'.format(layer_data['name']))
				for sublayer_data in sublayers:
					collect_overlays_summary(sublayer_data)
				overlays_summary.append(u'</div>')
			else:
				if 'visibility_scale_max' in layer_data:
					scale_visibility = 'Maximum (inclusive): {0}, Minimum (exclusive): {1}'.format(layer_data['visibility_scale_max'], layer_data['visibility_scale_min'])
				else:
					scale_visibility = ''
				template_data = format_template_data([
					layer_data['name'],
					layer_data['visible'],
					layer_data['queryable'],
					layer_data['extent'],
					layer_data['projection'],
					layer_data.get('geom_type', ''),
					scale_visibility,
					layer_data.get('labels', False),
					layer_data['provider_type'],
					", ".join([attribute.get('title', attribute['name']) for attribute in layer_data.get('attributes', [])]),
					layer_data['attribution']['title'] if 'attribution' in layer_data and 'title' in layer_data['attribution'] else '',
					layer_data['attribution']['url'] if 'attribution' in layer_data and 'url' in layer_data['attribution'] else '',
					layer_data['metadata']['title'],
					layer_data['metadata']['abstract'],
					layer_data['metadata']['keyword_list'],
				])
				layer_summary = u"""<h4>{0}</h4>
					<ul>
						<li><label>Visible:</label> {1}</li>
						<li><label>Queryable:</label> {2}</li>
						<li><label>Extent:</label> {3}</li>
						<li><label>CRS:</label> {4}</li>
						<li><label>Geometry type:</label> {5}</li>
						<li><label>Scale based visibility:</label> {6}</li>
						<li><label>Labels:</label> {7}</li>
						<li><label>Provider type:</label> {8}</li>
						<li><label>Attributes:</label> {9}</li>
						<li><label>Attribution:</label>
							<ul>
								<li><label>Title:</label> {10}</li>
								<li><label>URL:</label> {11}</li>
							</ul>
						</li>
						<li><label>Metadata:</label>
							<ul>
								<li><label>Title:</label> {12}</li>
								<li><label>Abstract:</label> {13}</li>
								<li><label>Keyword list:</label> {14}</li>
							</ul>
						</li>
					</ul>""".format(*template_data)
				overlays_summary.append(layer_summary)

		for layer_data in metadata['overlays']:
			collect_overlays_summary(layer_data)
		data['OVERLAY_LAYERS'] = u'\n'.join(overlays_summary)

		print_composers = []
		for composer_data in metadata['composer_templates']:
			template_data = (
				composer_data['name'],
				int(round(composer_data['width'])),
				int(round(composer_data['height']))
			)
			print_composers.append(u'<li>{0} ( {1} x {2}mm )</li>'.format(*template_data))
		data['PRINT_COMPOSERS'] = u'\n'.join(print_composers)

		html = u"""<html>
			<head>{0}</head>
			<body>""".format(CSS_STYLE)
		if self.run_in_gislab:
			html += u"""
				<h3>General information:</h3>
				<ul>
					<li><label>GIS.lab user:</label> {GISLAB_USER}</li>
					<li><label>GIS.lab ID:</label> {GISLAB_UNIQUE_ID}</li>
					<li><label>GIS.lab version:</label> {GISLAB_VERSION}</li>
				</ul>""".format(**format_template_data(data))
		html += u"""
				<h3>Project:</h3>
				<ul>
					<li><label>Title:</label> {TITLE}</li>
					<li><label>Abstract:</label> {ABSTRACT}</li>
					<li><label>Contact person:</label> {CONTACT_PERSON}</li>
					<li><label>Contact mail:</label> {CONTACT_MAIL}</li>
					<li><label>Contact organization:</label> {CONTACT_ORGANIZATION}</li>
					<li><label>Extent:</label> {EXTENT}</li>
					<li><label>Scales:</label> {SCALES}</li>
					<li><label>Resolutions:</label> {TILE_RESOLUTIONS}</li>
					<li><label>Projection:</label> {PROJECTION}</li>
					<li><label>Units:</label> {UNITS}</li>
					<li><label>Measure ellipsoid:</label> {MEASURE_ELLIPSOID}</li>
					<li><label>Use cache:</label> {USE_MAPCACHE}</li>
					<li><label>Authentication:</label> {AUTHENTICATION}</li>
					<li><label>Expiration date:</label> {EXPIRATION}</li>
					<li><label>Message text:</label> {MESSAGE_TEXT}</li>
					<li><label>Message validity:</label> {MESSAGE_VALIDITY}</li>
				</ul>
				<h3>Base layers:</h3>
					<div class="subcategory">
						<label>Default base layer:</label> {DEFAULT_BASE_LAYER}
						{BASE_LAYERS}
					</div>
				<h3>Overlay layers:</h3>
					<div class="subcategory">
					{OVERLAY_LAYERS}
					</div>
				<h3>Print composers:</h3>
				{PRINT_COMPOSERS}
			</body>
		</html>
		""".format(**format_template_data(data))
		self.dialog.config_summary.setHtml(html)

	def generate_confirmation_page(self):
		datasources = set()
		def collect_datasources(layer_node):
			for index in range(layer_node.childCount()):
				collect_datasources(layer_node.child(index))
			layer = layer_node.data(0, Qt.UserRole)
			if layer and layer_node.checkState(0) == Qt.Checked:
				datasources.add(layer.source())
		collect_datasources(self.dialog.overlaysTree.invisibleRootItem())

		html = u"""<html>
			<head>{0}</head>
			<body>
				<p><h4>Project '{1}' was successfully published.</h4></p>
				<p>Copy all project files to '~/Share/{5}' folder and visit <a href="{6}/share">{6}/share</a> page to load this project in GIS.lab Web.</p>

				<p><h4>Project files:</h4></p>
				<ul>
					<li><label>Project file:</label> {2}</li>
					<li><label>Project META file:</label> {3}</li>
				</ul>
				<p><h4>Data sources:</h4></p>
				<ul>{4}</ul>
			</body>
		</html>
		""".format(CSS_STYLE,
				self.metadata['title'],
				self.project.fileName(),
				os.path.splitext(self.project.fileName())[0] + '.meta',
				''.join(['<li>{0}</li>'.format(datasource) for datasource in datasources]),
				os.environ['USER'],
				GISLAB_WEB_URL
		)
		self.dialog.confirmation_info.setHtml(html)

	def _update_min_max_scales(self, resolutions):
		"""Updates available scales in Minimum/Maximum scale fields based on given resolutions."""
		if not resolutions:
			resolutions = get_tile_resolutions(DEFAULT_PROJECT_SCALES, self._map_units())
		resolutions = sorted(resolutions, reverse=True)
		scales = get_scales_from_resolutions(resolutions, self._map_units())
		index = self.dialog.min_scale.currentIndex()
		old_min_resolution = self.dialog.min_scale.itemData(index) if index != -1 else None
		index = self.dialog.max_scale.currentIndex()
		old_max_resolution = self.dialog.max_scale.itemData(index) if index != -1 else None

		self.dialog.min_scale.clear()
		self.dialog.max_scale.clear()
		for scale, resolution in zip(scales, resolutions):
			self.dialog.min_scale.addItem('1:{0}'.format(scale), Decimal(resolution))
			self.dialog.max_scale.addItem('1:{0}'.format(scale), Decimal(resolution))
		if old_min_resolution:
			for index, res in enumerate(resolutions):
				if res <= old_min_resolution:
					break
			self.dialog.min_scale.setCurrentIndex(index)
		else:
			self.dialog.min_scale.setCurrentIndex(len(scales)-1)

		if old_max_resolution:
			for index, res in enumerate(reversed(resolutions)):
				if res >= old_max_resolution:
					break
			index = len(resolutions)-1-index
			self.dialog.max_scale.setCurrentIndex(index)
		else:
			self.dialog.max_scale.setCurrentIndex(0)

	def setup_config_page_from_metadata(self):
		dialog = self.dialog
		metadata = self.current_metadata
		message = metadata.get('message')
		if message:
			dialog.message_text.insertPlainText(message.get('text', ''))
			valid_until = message.get('valid_until')
			dialog.message_valid_until.setDate(datetime.datetime.strptime(valid_until, "%d.%m.%Y"))
		expiration = metadata.get('expiration')
		if expiration:
			dialog.enable_expiration.setChecked(True)
			dialog.expiration.setDate(datetime.datetime.strptime(expiration, "%d.%m.%Y"))

		authentication = metadata.get('authentication')
		if authentication:
			# backward compatibility
			if type(authentication) is dict:
				if authentication.get('allow_anonymous') and not authentication.get('require_superuser'):
					dialog.authentication.setCurrentIndex(0)
				if not authentication.get('allow_anonymous'):
					dialog.authentication.setCurrentIndex(1)
			else:
				dialog.authentication.setCurrentIndex(AUTHENTICATION_OPTIONS.index(authentication) if authentication in AUTHENTICATION_OPTIONS else 1)
		project_extent = list(metadata['extent'])
		extent_buffer = metadata.get('extent_buffer', 0)
		if extent_buffer != 0:
			project_extent = [
				project_extent[0]+extent_buffer,
				project_extent[1]+extent_buffer,
				project_extent[2]-extent_buffer,
				project_extent[3]-extent_buffer
			]
		extent_index = dialog.extent_layer.findData(project_extent)
		if extent_index < 0:
			extent_index = 0
		dialog.extent_layer.setCurrentIndex(extent_index)
		dialog.use_mapcache.setChecked(metadata.get('use_mapcache') is True)
		dialog.extent_buffer.setValue(extent_buffer)
		# create list of all layers from layers metadata tree structure
		def extract_layers(layers_data, layers=None):
			if layers is None:
				layers = []
			for layer_data in layers_data:
				if 'layers' in layer_data:
					extract_layers(layer_data['layers'], layers)
				else:
					layers.append(layer_data)
			return layers

		if metadata.get('base_layers'):
			for base_layer in extract_layers(metadata['base_layers']):
				if base_layer['type'] == 'BLANK':
					dialog.blank.setChecked(True)
				elif base_layer['type'] == 'OSM':
					dialog.osm.setChecked(True)
				elif base_layer['type'] == 'google':
					for index, glayer in enumerate(GOOGLE_LAYERS, 1):
						if glayer['name'] == base_layer['name']:
							dialog.google.setCurrentIndex(index);
							break
				if base_layer['visible']:
					dialog.default_baselayer.setCurrentIndex(dialog.default_baselayer.findData(base_layer['name']))

		overlays_data = extract_layers(metadata['overlays'])
		project_overlays = [layer_data['name'] for layer_data in overlays_data]
		hidden_overlays = [layer_data['name'] for layer_data in overlays_data if layer_data.get('hidden')]
		overlays_with_export_to_drawings = [layer_data['name'] for layer_data in overlays_data if layer_data.get('export_to_drawings')]
		def uncheck_excluded_layers(widget):
			if widget.data(0, Qt.UserRole):
				widget.setCheckState(0, Qt.Checked if widget.text(0) in project_overlays else Qt.Unchecked)
				widget.setCheckState(1, Qt.Checked if widget.text(0) in hidden_overlays else Qt.Unchecked)
				if widget.data(2, Qt.CheckStateRole) != None:
					widget.setCheckState(2, Qt.Checked if widget.text(0) in overlays_with_export_to_drawings else Qt.Unchecked)
			else:
				for index in range(widget.childCount()):
					uncheck_excluded_layers(widget.child(index))
		uncheck_excluded_layers(dialog.overlaysTree.invisibleRootItem())

		max_res = metadata['tile_resolutions'][0]
		min_res = metadata['tile_resolutions'][-1]
		min_scale, max_scale = get_scales_from_resolutions(to_decimal_array([min_res, max_res]), self._map_units())
		dialog.min_scale.setCurrentIndex(dialog.min_scale.findText("1:{0}".format(min_scale)))
		dialog.max_scale.setCurrentIndex(dialog.max_scale.findText("1:{0}".format(max_scale)))

	def run(self):
		if self.dialog and self.dialog.isVisible():
			return
		self.project = QgsProject.instance()
		dialog_filename = os.path.join(self.plugin_dir, "publish_dialog.ui")
		dialog = PyQt4.uic.loadUi(dialog_filename)
		dialog.tabWidget.setCurrentIndex(0)
		dialog.setButtonText(QWizard.CommitButton, "Publish")
		#dialog.wizard_page4.setButtonText(QWizard.FinishButton, "Ok")
		dialog.wizard_page3.setCommitPage(True)
		dialog.wizard_page4.setButtonText(QWizard.CancelButton, "Close")
		dialog.wizard_page1.validatePage = self.validate_config_page
		dialog.wizard_page2.validatePage = self.validate_topics_page
		dialog.wizard_page3.validatePage = self.publish_project
		self.dialog = dialog
		self.topics_initialized = False
		map_canvas = self.iface.mapCanvas()

		def expiration_toggled(checked):
			self.dialog.expiration.setEnabled(checked)
		dialog.enable_expiration.toggled.connect(expiration_toggled)
		dialog.expiration.setDate(datetime.date.today() + datetime.timedelta(days=1))

		resolutions = self._project_layers_resolutions()
		self._update_min_max_scales(resolutions)

		def blank_toggled(checked):
			if checked:
				self.dialog.default_baselayer.insertItem(0, 'Blank', 'BLANK')
			else:
				self.dialog.default_baselayer.removeItem(0)

		def osm_toggled(checked, project_resolutions=resolutions):
			resolutions = set(project_resolutions)
			position = 1 if self.dialog.blank.isChecked() else 0
			if checked:
				self.dialog.default_baselayer.insertItem(position, OSM_LAYER['title'], OSM_LAYER['name'])
				resolutions.update(OSM_LAYER['resolutions'])
			else:
				self.dialog.default_baselayer.removeItem(position)

			if self.dialog.google.currentIndex() > 0:
				resolutions.update(GOOGLE_LAYERS[0]['resolutions'])
			self._update_min_max_scales(resolutions)

		def google_layer_changed(index, project_resolutions=resolutions):
			resolutions = set(project_resolutions)
			position = 1 if self.dialog.blank.isChecked() else 0
			if self.dialog.osm.isChecked():
				position += 1
				resolutions.update(OSM_LAYER['resolutions'])

			google_layers = [self.dialog.google.itemText(i) for i in range(1, 5)]
			contains_google_layer = self.dialog.default_baselayer.itemText(position) in google_layers
			if index > 0:
				google_layer = GOOGLE_LAYERS[index-1]
				if contains_google_layer:
					self.dialog.default_baselayer.setItemText(position, self.dialog.google.currentText())
					self.dialog.default_baselayer.setItemData(position, google_layer['name'])
				else:
					self.dialog.default_baselayer.insertItem(position, self.dialog.google.currentText(), google_layer['name'])
				resolutions.update(google_layer['resolutions'])
			elif contains_google_layer:
				self.dialog.default_baselayer.removeItem(position)
			self._update_min_max_scales(resolutions)

		dialog.blank.toggled.connect(blank_toggled)
		dialog.osm.toggled.connect(osm_toggled)
		dialog.google.currentIndexChanged.connect(google_layer_changed)

		def scales_changed(index):
			self._check_publish_constrains()
		dialog.min_scale.currentIndexChanged.connect(scales_changed)
		dialog.max_scale.currentIndexChanged.connect(scales_changed)

		projection = map_canvas.mapRenderer().destinationCrs().authid()
		dialog.osm.setEnabled(projection == 'EPSG:3857')
		dialog.google.setEnabled(projection == 'EPSG:3857')

		dialog.extent_layer.addItem("All layers", list(map_canvas.fullExtent().toRectF().getCoords()))
		for layer in self.iface.legendInterface().layers():
			if self._is_base_layer_for_publish(layer):
				dialog.default_baselayer.addItem(layer.name(), layer.name())
			if self._is_base_layer_for_publish(layer) or self._is_overlay_layer_for_publish(layer):
				dialog.extent_layer.addItem(layer.name(), list(map_canvas.mapRenderer().layerExtentToOutputExtent(layer, layer.extent()).toRectF().getCoords()))

		dialog.message_valid_until.setDate(datetime.date.today() + datetime.timedelta(days=1))

		self._check_publish_constrains()
		dialog.overlaysTree.header().setResizeMode(0, QHeaderView.Stretch)
		dialog.overlaysTree.header().setVisible(True)
		self.base_layers_tree, self.overlay_layers_tree = self._get_project_layers()

		def create_layer_widget(node):
			widget = QTreeWidgetItem()
			widget.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
			sublayers_widgets = []
			for child in node.children:
				sublayer_widget = create_layer_widget(child)
				if sublayer_widget:
					sublayers_widgets.append(sublayer_widget)
			if sublayers_widgets:
				widget.setText(0, node.name)
				widget.setCheckState(0, Qt.Unchecked)
				widget.addChildren(sublayers_widgets)
			elif node.layer:
				layer = node.layer
				widget.setText(0, layer.name())
				widget.setData(0, Qt.UserRole, layer)
				widget.setCheckState(0, Qt.Checked)
				widget.setCheckState(1, Qt.Unchecked)
				# remove 'Export to drawings' checkbox if raster layer
				widget.setData(2, Qt.CheckStateRole, Qt.Checked if layer.type() == QgsMapLayer.VectorLayer else None);
			return widget
		if self.overlay_layers_tree:
			dialog.overlaysTree.addTopLevelItems(create_layer_widget(self.overlay_layers_tree).takeChildren())

		metadata_filename = os.path.splitext(self.project.fileName())[0] + '.meta'
		self.current_metadata = None
		if os.path.exists(metadata_filename):
			with open(metadata_filename, "r") as f:
				self.current_metadata = json.load(f)
			try:
				self.setup_config_page_from_metadata()
			except:
				QMessageBox.warning(None, 'Warning', 'Failed to load settings from last published version')
		dialog.show()
		dialog.exec_()
