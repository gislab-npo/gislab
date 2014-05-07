# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GIS.lab Web plugin
 Publish your projects into GIS.lab Web application
                              -------------------
        begin                : 2014-01-09
        copyright            : (C) 2014 by Marcel Dancak
        email                : marcel.dancak@gista.sk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation version 3.                               *
 *                                                                         *
 ***************************************************************************/
"""

import json
import time
import os.path
import subprocess
from urllib import urlencode
from urlparse import parse_qs

# Import the PyQt and QGIS libraries
import PyQt4.uic
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Initialize Qt resources from file resources.py
import resources_rc


MSG_ERROR = "Error"
MSG_WARNING = "Warning"

class Node(object):
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


def get_tile_resolutions(scales, units, dpi=96):
	"""Helper function to compute OpenLayers tile resolutions."""

	dpi = float(dpi)
	factor = {'feett': 12.0, 'meters': 39.3701, 'miles': 63360.0, 'degrees': 4374754.0}

	inches = 1.0 / dpi
	monitor_l = inches / factor[units]

	resolutions = []
	for m in scales:
		resolutions.append(monitor_l * int(m))
	return resolutions


def extent_to_list(extent):
	return [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()]


OSM_LAYER = {'name': 'OSM', 'type': 'OSM', 'title': 'Open Street Map', 'resolutions': [156543.03390625, 78271.516953125, 39135.7584765625, 19567.87923828125, 9783.939619140625, 4891.9698095703125, 2445.9849047851562, 1222.9924523925781, 611.4962261962891, 305.74811309814453, 152.87405654907226, 76.43702827453613, 38.218514137268066, 19.109257068634033, 9.554628534317017, 4.777314267158508, 2.388657133579254, 1.194328566789627, 0.5971642833948135]}

google_resolutions = [156543.03390625, 78271.516953125, 39135.7584765625, 19567.87923828125, 9783.939619140625, 4891.9698095703125, 2445.9849047851562, 1222.9924523925781, 611.4962261962891, 305.74811309814453, 152.87405654907226, 76.43702827453613, 38.218514137268066, 19.109257068634033, 9.554628534317017, 4.777314267158508]
GOOGLE_LAYERS = {
	'GHYBRID': {'name': 'GHYBRID', 'type': 'google', 'title': 'Google Hybrid', 'resolutions': google_resolutions},
	'GROADMAP': {'name': 'GROADMAP', 'type': 'google', 'title': 'Google Roadmap', 'resolutions': google_resolutions},
	'GSATELLITE': {'name': 'GSATELLITE', 'type': 'google', 'title': 'Google Satellite', 'resolutions': google_resolutions},
	'GTERRAIN': {'name': 'GTERRAIN', 'type': 'google', 'title': 'Google Terrain', 'resolutions': google_resolutions},
}

class WebGisPlugin:

	dialog = None
	project = None

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

		self.project = QgsProject.instance()

	def initGui(self):
		# Create action that will start plugin configuration
		self.action = QAction(
			QIcon(":/plugins/webgisplugin/icon.png"),
			u"Publish in GIS.lab Web", self.iface.mainWindow())
		# connect the action to the run method
		self.action.triggered.connect(self.run)

		# Add toolbar button and menu item
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu(u"&GIS.lab Web", self.action)

		self.project.readProject.connect(self._check_plugin_state)
		self.project.projectSaved.connect(self._check_plugin_state)
		self.iface.newProjectCreated.connect(self._check_plugin_state)
		self._check_plugin_state()

	def unload(self):
		# Remove the plugin menu item and icon
		self.iface.removePluginMenu(u"&GIS.lab Web", self.action)
		self.iface.removeToolBarIcon(self.action)
		
		self.project.projectSaved.disconnect()
		self.project.readProject.disconnect()
		self.iface.newProjectCreated.disconnect()

	def _check_plugin_state(self, *args):
		filepath = self.project.fileName()
		self.action.setEnabled("/Share/" in filepath)

	def _show_messages(self, messages):
		dialog = self.dialog
		table = dialog.info_table
		if not messages:
			dialog.messages_group.setVisible(False)
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

	def _check_publish_constrains(self):
		map_canvas = self.iface.mapCanvas()
		all_layers = [layer.name() for layer in self.iface.legendInterface().layers()]
		messages = []
		#messages = [(MSG_ERROR, "Err1"), (MSG_WARNING, "Brr2"), (MSG_WARNING, "Brr1 fshfjh sjfs jgdhj erssejr hesuseuthrjfghdj jdj dj sdu bnbbnbnbb rtr4r45 iioopoppoqqwases")]
		if self.project.isDirty():
			messages.append((MSG_ERROR, u"Project has been modified. Save it (Project > Save)."))

		crs_transformation, ok = self.project.readEntry("SpatialRefSys", "/ProjectionsEnabled")
		if not ok or not crs_transformation:
			messages.append((MSG_ERROR, u"'On the fly' CRS transformation not enabled ('Project > Project Properties > CRS')."))
		self._show_messages(messages)
		for msg_type, msg_text in messages:
			if msg_type == MSG_ERROR:
				self.dialog.publish_btn.setEnabled(False)
				return False
		self.dialog.publish_btn.setEnabled(True)
		return True

	def _is_overlay_layer_for_publish(self, layer):
		return layer.type() == QgsMapLayer.VectorLayer or (layer.type() == QgsMapLayer.RasterLayer and layer.providerType() != "wms")

	def _is_base_layer_for_publish(self, layer, resolutions=None):
		return layer.type() == QgsMapLayer.RasterLayer and layer.providerType() == "wms"

	def _filter_layer_visible_resolutions(self, resolutions, layer, units):
		if layer.hasScaleBasedVisibility():
			max_scale_exclusive = layer.maximumScale()
			min_scale_inclusive = layer.minimumScale()
			max_resolution_exclusive, min_resolution_inclusive = get_tile_resolutions([max_scale_exclusive, min_scale_inclusive], units)
			return filter(lambda res: res >= min_resolution_inclusive and res < max_resolution_exclusive, resolutions)
		return resolutions

	def _wmsc_layers_resolutions(self, layer, units):
		layer_resolutions = layer.dataProvider().property('resolutions')
		if layer_resolutions:
			if layer.hasScaleBasedVisibility():
				layer_resolutions = self._filter_layer_visible_resolutions(layer_resolutions, layer, units)
			if layer_resolutions:
				return sorted(layer_resolutions, reverse=True)
			return []
		return None


	def _publish_project(self):
		if not self._check_publish_constrains():
			return
		dialog = self.dialog
		project = self.project.fileName().split("/Share/")[1]
		map_canvas = self.iface.mapCanvas()
		legend_iface = self.iface.legendInterface()

		extent = [round(coord, 3) for coord in map_canvas.extent().toRectF().getCoords()]
		get_params = [('PROJECT', project)]

		scales, ok = self.project.readListEntry("Scales", "/ScalesList")
		if ok and scales:
			scales = [scale.split(":")[-1] for scale in scales]

		units = {0: 'meters', 1: 'feet', 2: 'degrees', 3: 'unknown', 7: 'miles'}[map_canvas.mapUnits()]

		get_params.append(('EXTENT', ','.join(map(str, extent))))
		drawings = dialog.drawings.text()
		if drawings:
			get_params.append(('DRAWINGS', drawings.replace(" ", "")))

		metadata = {
			'title': self.project.readEntry("WMSServiceTitle", "/")[0] or self.project.title(),
			'abstract': self.project.readEntry("WMSServiceAbstract", "/")[0],
			'contact_person': self.project.readEntry("WMSContactPerson", "/")[0],
			'contact_organization': self.project.readEntry("WMSContactOrganization", "/")[0],
			'contact_mail': self.project.readEntry("WMSContactMail", "/")[0],
			'authentication': {
				'allow_anonymous': False,
				'require_superuser': False
			},
			'use_mapcache': False,
			'publish_date_unix': int(time.time()),
			'publish_date': time.ctime(),
		}
		renderer_context = map_canvas.mapRenderer().rendererContext()
		selection_color = renderer_context.selectionColor()
		canvas_color = map_canvas.canvasColor()
		metadata.update({
			'extent': extent_to_list(map_canvas.fullExtent()),
			'projection': map_canvas.mapRenderer().destinationCrs().authid(),
			#'scales': scales,
			'selection_color': '{0}{1:02x}'.format(selection_color.name(), selection_color.alpha()),
			'canvas_color': '{0}{1:02x}'.format(canvas_color.name(), canvas_color.alpha()),
			'units': units,
			'measure_ellipsoid': self.project.readEntry("Measure", "/Ellipsoid", "")[0],
			'position_precision': {
				'automatic': self.project.readBoolEntry("PositionPrecision", "/Automatic")[0],
				'decimal_places': self.project.readNumEntry("PositionPrecision", "/DecimalPlaces")[0]
			}
		})

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

		special_base_layers = []
		#if dialog.blank.isChecked():
		#	special_base_layers.append({'name': 'Blank', 'type': 'BLANK'})
		if metadata['projection'].upper() == 'EPSG:3857':
			if dialog.osm.isChecked():
				special_base_layers.append(OSM_LAYER)
			if dialog.google.currentIndex() > 0:
				google_layer_name = 'G{0}'.format(dialog.google.currentText().upper())
				special_base_layers.append(GOOGLE_LAYERS[google_layer_name])

		# Calculate project resolutions as an union of resolutions calculated from project scales and resolutions of WMSC layers.
		# When no project resolutions can be calculated, default scales will be used.
		project_tile_resolutions = set()
		if scales:
			project_tile_resolutions.update(get_tile_resolutions(sorted(scales, reverse=True), units))

		# collect set of all resolutions from special base layers and WMSC base layers
		for special_base_layer in special_base_layers:
			resolutions = special_base_layer.get('resolutions')
			if resolutions:
				project_tile_resolutions.update(resolutions)

		wmsc_layers_resolutions = set()
		for layer in base_layers.itervalues():
			layer_resolutions = self._wmsc_layers_resolutions(layer, units)
			if layer_resolutions:
				project_tile_resolutions.update(layer_resolutions)

		if not project_tile_resolutions:
			project_tile_resolutions = get_tile_resolutions(DEFAULT_PROJECT_SCALES, units) #TODO: or always meters?
		project_tile_resolutions = sorted(project_tile_resolutions, reverse=True)
		metadata['tile_resolutions'] = project_tile_resolutions

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

		# create base layers metadata
		def base_layers_data(node):
			if node.children:
				sublayers_data = [base_layers_data(child) for child in node.children]
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
					'visible': legend_iface.isLayerVisible(layer),
					'extent': extent_to_list(map_canvas.mapRenderer().layerExtentToOutputExtent(layer, layer.extent())),
					'wms_layers': source_params['layers'][0].split(','),
					'projection': source_params['crs'][0],
					'format': source_params['format'][0],
					'url': source_params['url'][0],
					'dpi': layer.dataProvider().dpi()
				}
				layer_resolutions = layer.dataProvider().property('resolutions')
				if layer_resolutions:
					layer_resolutions = self._wmsc_layers_resolutions(layer, units)
					min_resolution = layer_resolutions[-1]
					max_resolution = layer_resolutions[0]
					upper_resolutions = filter(lambda res: res > max_resolution, project_tile_resolutions)
					lower_resolutions = filter(lambda res: res < min_resolution, project_tile_resolutions)
					layer_data.update({
						'type': 'WMSC',
						'min_resolution': min_resolution,
						'max_resolution': max_resolution,
						'resolutions': upper_resolutions + layer_resolutions + lower_resolutions
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

		if base_layers_tree:
			base_layers_metadata = base_layers_data(base_layers_tree)
		else:
			base_layers_metadata = {'layers': []}

		# insert special base layers metadata
		for special_base_layer in special_base_layers:
			if not special_base_layer.get('resolutions'):
				special_base_layer['resolutions'] = project_tile_resolutions
			base_layers_metadata['layers'].insert(0, special_base_layer)

		metadata['base_layers'] = base_layers_metadata.get('layers')

		# encode layers grouped by their parents
		def encode_layers_group(layers_nodes):
			categories = []
			node = layers_nodes[0]
			while node.parent:
				categories.insert(0, node.parent.name)
				node = node.parent
			location = "/".join(categories) if categories else "/"
			encoded_layers = ["{0}:{1}".format(node.layer.name(), "1" if legend_iface.isLayerVisible(node.layer) else "0") for node in layers_nodes]
			return "{0}/{1}".format(location, ";".join(encoded_layers))

		# find largest groups of sibling nodes and encode them for BASE parameter value
		base_param_parts = []
		if base_layers_tree:
			base_group = []
			def base_node_callback(node):
				if not node.children:
					base_group.append(node)
				else:
					if base_group:
						base_param_parts.append(encode_layers_group(base_group))
						del base_group[:]
					for child in node.children:
						base_node_callback(child)
					if base_group:
						base_param_parts.append(encode_layers_group(base_group))
						del base_group[:]
			base_node_callback(base_layers_tree)


		if special_base_layers:
			base_param_parts.insert(0, "/{0}".format(";".join([special_base_layer['name'] for special_base_layer in special_base_layers])))

		base_param = ";".join(base_param_parts)
		if base_param:
			get_params.append(('BASE', base_param))


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

		non_identifiable_layers = self.project.readListEntry("Identify", "/disabledLayers")[0] or []

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
				transformation = map_canvas.mapRenderer().transformation(layer)
				extent = transformation.transformBoundingBox(layer.extent())
				layer_data = {
					'name': layer.name(),
					'provider_type': layer.providerType(),
					'extent': extent_to_list(map_canvas.mapRenderer().layerExtentToOutputExtent(layer, layer.extent())),
					'visible': legend_iface.isLayerVisible(layer),
					'queryable': layer.id() not in non_identifiable_layers
				}
				if layer.attribution():
					layer_data['attribution'] = {
						'title': layer.attribution(),
						'url': layer.attributionUrl()
					}
				if layer.hasGeometryType():
					layer_data['geom_type'] = ('POINT', 'LINE', 'POLYGON')[layer.geometryType()]
				fields = layer.pendingFields()
				attributes_data = []
				excluded_attributes = layer.excludeAttributesWMS()
				for index, field in enumerate(fields):
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
				return layer_data
		metadata['overlays'] = create_overlays_data(overlay_layers_tree).get('layers')

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

		# create metadata file
		metadata_filename = os.path.splitext(self.project.fileName())[0] + '.meta'
		with open(metadata_filename, "w") as f:
			json.dump(metadata, f, indent=2)

		link = 'http://web.gis.lab/?{0}'.format(urlencode(get_params))
		subprocess.Popen([r'firefox', '-new-tab', link])
		dialog.close()

	def _table_size_hint(self):
		table = self.dialog.info_table
		height = table.horizontalHeader().height()
		for row in range(table.rowCount()):
			height += table.rowHeight(row)
		#return QSize(0, height+2)
		return QSize(table.width(), height+2)

	# run method that performs all the real work
	def run(self):
		if self.dialog and self.dialog.isVisible():
			return
		dialog_filename = os.path.join(self.plugin_dir, "publish_dialog.ui")
		dialog = PyQt4.uic.loadUi(dialog_filename)
		dialog.publish_btn.released.connect(self._publish_project)
		#dialog.check_btn.released.connect(self._check_publish_constrains)
		dialog.info_table.sizeHint = self._table_size_hint
		self.dialog = dialog

		self._check_publish_constrains()
		#self.dialog.info_table.resize(self._table_size_hint())
		self.dialog.adjustSize()
		#self.dialog.info_table.adjustSize()
		self.dialog.show()
		self.dialog.exec_()


# vim: set ts=4 sts=4 sw=4 noet:
