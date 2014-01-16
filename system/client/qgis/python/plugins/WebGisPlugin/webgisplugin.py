# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WebGIS plugin
                                 A QGIS plugin
 Publish your projects into WebGIS application
                              -------------------
        begin                : 2014-01-09
        copyright            : (C) 2014 by GISTA s.r.o.
        email                : info@gista.sk
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

# Import the PyQt and QGIS libraries
import PyQt4.uic
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Initialize Qt resources from file resources.py
import resources_rc


MSG_ERROR = "Error"
MSG_WARNING = "Warning"

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
			u"Publish project", self.iface.mainWindow())
		# connect the action to the run method
		self.action.triggered.connect(self.run)

		# Add toolbar button and menu item
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu(u"&WebGIS", self.action)

		self.project.readProject.connect(self._check_plugin_state)
		self.project.projectSaved.connect(self._check_plugin_state)
		self.iface.newProjectCreated.connect(self._check_plugin_state)
		self._check_plugin_state()

	def unload(self):
		# Remove the plugin menu item and icon
		self.iface.removePluginMenu(u"&WebGIS", self.action)
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
			messages.append((MSG_ERROR, u"Project has been modified, please save it and try again."))

		project_basename = os.path.splitext(os.path.basename(self.project.fileName()))[0]
		if project_basename in all_layers:
			messages.append((MSG_ERROR, u"Project's filename cannot match any layer name, please rename it."))

		crs_transformation, ok = self.project.readEntry("SpatialRefSys", "/ProjectionsEnabled")
		if not ok or not crs_transformation:
			messages.append((MSG_ERROR, u"'On the fly' CRS transformation not enabled."))
		self._show_messages(messages)
		for msg_type, msg_text in messages:
			if msg_type == MSG_ERROR:
				self.dialog.publish_btn.setEnabled(False)
				return False
		self.dialog.publish_btn.setEnabled(True)
		return True

	def _publish_project(self):
		if not self._check_publish_constrains():
			return
		dialog = self.dialog
		project = self.project.fileName().split("/Share/")[1]
		map_canvas = self.iface.mapCanvas()
		all_layers = [layer.name() for layer in self.iface.legendInterface().layers()]
		extent = [round(coord, 3) for coord in map_canvas.extent().toRectF().getCoords()]
		get_params = {
			'PROJECT': project,
			'LAYERS': ','.join(all_layers),
			'EXTENT': ','.join(map(str, extent)),
		}
		if dialog.osm.isChecked():
			get_params['OSM'] = 'true'
		scales, ok = self.project.readListEntry("Scales", "/ScalesList")
		if ok and scales:
			scales = [scale.split(":")[-1] for scale in scales]
			get_params['SCALES'] = ','.join(scales)
		if dialog.google.currentIndex() > 0:
			get_params['GOOGLE'] = dialog.google.currentText().upper()
		balls = dialog.balls.text()
		if balls:
			get_params['BALLS'] = balls.replace(" ", "")

		if map_canvas.layerCount() < len(all_layers):
			get_params['VISIBLE'] = ','.join([layer.name() for layer in map_canvas.layers()])
		link = 'http://web.gis.lab/?{0}'.format("&".join(["{0}={1}".format(name, value) for name, value in get_params.iteritems()]))
		#print "Starting firefox ...", link
		subprocess.Popen([r'firefox', '-new-tab', link])

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

