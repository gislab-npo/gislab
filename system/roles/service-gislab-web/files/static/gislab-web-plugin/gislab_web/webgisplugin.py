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
import subprocess
from decimal import Decimal
from urllib import urlencode
from urlparse import parse_qs

# Import the PyQt and QGIS libraries
import PyQt4.uic
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Initialize Qt resources from file resources.py
import resources_rc

from utils import *
from project import ProjectPage
from topics import TopicsPage
from drawing import DrawingPage
from summary import SummaryPage
from confirmation import ConfirmationPage


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

	def is_overlay_layer_for_publish(self, layer):
		"""Checks whether layer could be published as overlay layer."""
		return (layer.type() == QgsMapLayer.VectorLayer or
			(layer.type() == QgsMapLayer.RasterLayer and layer.providerType() != "wms"))

	def is_base_layer_for_publish(self, layer):
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

	def map_units(self):
		"""Returns current map units name ('meters', 'feet', 'degrees', 'miles' or 'unknown')."""
		map_canvas = self.iface.mapCanvas()
		return {0: 'meters', 1: 'feet', 2: 'degrees', 3: 'unknown', 7: 'miles'}[map_canvas.mapUnits()]

	def project_layers_resolutions(self):
		"""Calculate project resolutions as an union of resolutions calculated
		from project scales and resolutions of all WMSC layers."""
		project_tile_resolutions = set()
		units = self.map_units()

		# collect set of all resolutions from WMSC base layers
		base_layers = {layer.id(): layer for layer in self.iface.legendInterface().layers() if self.is_base_layer_for_publish(layer)}
		for layer in base_layers.itervalues():
			layer_resolutions = self._wmsc_layer_resolutions(layer, units)
			if layer_resolutions:
				project_tile_resolutions.update(layer_resolutions)

		wmsc_layers_scales = get_scales_from_resolutions(project_tile_resolutions, self.map_units())
		scales, ok = self.project.readListEntry("Scales", "/ScalesList")
		if ok and scales:
			scales = [int(scale.split(":")[-1]) for scale in scales]
			# filter duplicit scales
			scales = filter(lambda scale: scale not in wmsc_layers_scales, scales)
			project_tile_resolutions.update(get_tile_resolutions(sorted(scales, reverse=True), units))

		project_tile_resolutions = sorted(project_tile_resolutions, reverse=True)
		return project_tile_resolutions

	def get_project_layers(self):
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
		base_layers = {layer.id(): layer for layer in legend_iface.layers() if self.is_base_layer_for_publish(layer)}

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
		overlay_layers = {layer.id(): layer for layer in legend_iface.layers() if self.is_overlay_layer_for_publish(layer)}
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

	def collect_metadata(self):
		metadata = {}
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

		page_id = 0
		while page_id < self.dialog.currentId():
			page = self.dialog.page(page_id)
			metadata.update(page.handler.get_metadata() or {})
			page_id = page.nextId()
		self.metadata = metadata
		return metadata

	def publish_project(self, metadata):
		"""Creates project metadata file."""

		# create metadata file
		metadata_filename = os.path.splitext(self.project.fileName())[0] + '.meta'
		with open(metadata_filename, "w") as f:
			def decimal_default(obj):
				if isinstance(obj, Decimal):
					return float(obj)
				raise TypeError
			json.dump(metadata, f, indent=2, default=decimal_default)

		return True


	def run(self):
		if self.dialog and self.dialog.isVisible():
			return
		self.project = QgsProject.instance()
		current_metadata = None
		metadata_filename = os.path.splitext(self.project.fileName())[0] + '.meta'
		if os.path.exists(metadata_filename):
			with open(metadata_filename, "r") as f:
				current_metadata = json.load(f)

		dialog_filename = os.path.join(self.plugin_dir, "publish_dialog.ui")
		dialog = PyQt4.uic.loadUi(dialog_filename)
		self.dialog = dialog
		dialog.tabWidget.setCurrentIndex(0)
		dialog.setButtonText(QWizard.CommitButton, "Publish")
		#dialog.wizard_page5.setButtonText(QWizard.FinishButton, "Ok")
		dialog.wizard_page4.setCommitPage(True)
		dialog.wizard_page5.setButtonText(QWizard.CancelButton, "Close")

		ProjectPage(self, dialog.wizard_page1, current_metadata)
		TopicsPage(self, dialog.wizard_page2, current_metadata)
		drawing_page = DrawingPage(self, dialog.wizard_page3, current_metadata)
		def after_topics_page():
			# skip page 'export of layers to drawing' when it is not needed
			return 2 if drawing_page.get_drawing_layers() else 3
		dialog.wizard_page2.nextId = after_topics_page

		SummaryPage(self, dialog.wizard_page4, current_metadata)
		ConfirmationPage(self, dialog.wizard_page5, current_metadata)

		"""
		self.current_metadata = None
		if os.path.exists(metadata_filename):
			with open(metadata_filename, "r") as f:
				self.current_metadata = json.load(f)
			try:
				self.setup_config_page_from_metadata()
			except:
				QMessageBox.warning(None, 'Warning', 'Failed to load settings from last published version')
		"""
		dialog.show()
		dialog.exec_()
