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

import os.path
import subprocess
from urllib import urlencode

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

	def __init__(self, name, children=None):
		self.name = name
		self.children = []
		if children:
			self.append(*children)

	def append(self, *nodes):
		for node in nodes:
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


METADATA_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Metadata>
	<Authentication>
		<AllowAnonymous>{anonymous}</AllowAnonymous>
		<RequireSuperuser>{superuser}</RequireSuperuser>
	</Authentication>
</Metadata>
"""

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

	def _is_base_layer_for_publish(self, layer):
		return layer.type() == QgsMapLayer.RasterLayer and layer.providerType() == "wms"

	def _publish_project(self):
		if not self._check_publish_constrains():
			return
		dialog = self.dialog
		project = self.project.fileName().split("/Share/")[1]
		map_canvas = self.iface.mapCanvas()
		legend_iface = self.iface.legendInterface()

		extent = [round(coord, 3) for coord in map_canvas.extent().toRectF().getCoords()]
		get_params = [('PROJECT', project)]

		layers_reletionship = legend_iface.groupLayerRelationship()
		layers_root = Node('')
		for parent_name, child_names in layers_reletionship:
			parent = layers_root.find(parent_name)
			if not parent:
				parent = Node(parent_name)
				layers_root.append(parent)
			parent.append(*child_names)

		# filter base layers only
		base_layers = [layer for layer in legend_iface.layers() if self._is_base_layer_for_publish(layer)]
		# asign base layers to nodes
		for layer in base_layers:
			node = layers_root.find(layer.id())
			node.layer = layer

		# encode layers grouped by their parents
		base_param_parts = []
		def encode_layers_group(layers_nodes):
			categories = []
			node = layers_nodes[0]
			while node.parent:
				categories.insert(0, node.parent.name)
				node = node.parent
			location = "/".join(categories) if categories else "/"
			encoded_layers = ["{0}:{1}".format(node.layer.name(), "1" if legend_iface.isLayerVisible(node.layer) else "0") for node in layers_nodes]
			return "{0}/{1}".format(location, ";".join(encoded_layers))

		base_group = []
		def visit_node(node, base_group=base_group):
			for child in node.children:
				visit_node(child, base_group=base_group)
			if not node.children:
				if node.layer in base_layers:
					base_group.append(node)
			else:
				if base_group:
					base_param_parts.append(encode_layers_group(base_group))
				del base_group[:]
		visit_node(layers_root)
		if base_group:
			base_param_parts.append(encode_layers_group(base_group))

		special_base_layers = []
		if dialog.osm.isChecked():
			special_base_layers.append('OSM')
		if dialog.google.currentIndex() > 0:
			special_base_layers.append('G{0}'.format(dialog.google.currentText().upper()))
		if special_base_layers:
			base_param_parts.insert(0, "/{0}".format(";".join(special_base_layers)))

		base_param = ";".join(base_param_parts)
		if base_param:
			get_params.append(('BASE', base_param))

		scales, ok = self.project.readListEntry("Scales", "/ScalesList")
		if ok and scales:
			scales = [scale.split(":")[-1] for scale in scales]
			get_params.append(('SCALES', ','.join(scales)))

		get_params.append(('EXTENT', ','.join(map(str, extent))))
		drawings = dialog.drawings.text()
		if drawings:
			get_params.append(('DRAWINGS', drawings.replace(" ", "")))

		link = 'http://web.gis.lab/?{0}'.format(urlencode(get_params))

		# create metadata file
		metadata_filename = self.project.fileName() + '.meta'
		with open(metadata_filename, "w") as f:
			f.write(METADATA_TEMPLATE.format(
				anonymous=False,
				superuser=False
			))
		#print "Starting firefox ...", link
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
