# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GIS.lab Web plugin
 Publish your projects into GIS.lab Web application
 ***************************************************************************/
"""

import os

# Import the PyQt and QGIS libraries
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from wizard import PublishPage


class DrawingPage(PublishPage):

	def get_drawing_filename(self):
		return "{0}_{1}.geojson".format(os.path.splitext(self.plugin.project.fileName())[0], "drawing")

	def get_drawing_layers(self, node=None):
		if node is None:
			node = self.plugin.get_project_layers()
		layers = []
		for child in node.children:
			layers.extend(self.get_drawing_layers(child))
		if node.layer:
			layer = node.layer
			layers_model = self.dialog.treeView.model()
			layer_widget = layers_model.findItems(layer.name(), Qt.MatchExactly | Qt.MatchRecursive)[0]
			if layer_widget.checkState() == Qt.Checked and layers_model.columnItem(layer_widget, 1).checkState() == Qt.Checked:
				layers.append(layer)
		return layers

	def initialize(self, metadata=None):
		vector_layers = [layer for layer in self.plugin.iface.legendInterface().layers() if layer.type() == QgsMapLayer.VectorLayer]
		last_config_layers = metadata.get('layers_drawing', {}).get('layers', {}) if metadata else {}
		layout = QVBoxLayout()
		for layer in vector_layers:
			layer_name = layer.name()
			row_layout = QHBoxLayout()
			row_layout.setObjectName(layer_name)
			row_layout.setContentsMargins(0, 0, 0, 0)
			title_attribute = QComboBox()
			title_attribute.setObjectName('title')
			description_attribute = QComboBox()
			description_attribute.setObjectName('description')
			title_attribute.addItem('-', '')
			description_attribute.addItem('-', '')
			fields = layer.pendingFields()
			excluded_attributes = layer.excludeAttributesWMS()
			for index in range(fields.count()):
				field = fields.field(index)
				if field.name() in excluded_attributes:
					continue

				name = field.name()
				display = layer.attributeDisplayName(index)
				title_attribute.addItem(display, name)
				description_attribute.addItem(display, name)

			if layer_name in last_config_layers:
				previous_title_index = title_attribute.findData(last_config_layers[layer_name]['title_attribute'])
				previous_description_index = description_attribute.findData(last_config_layers[layer_name]['description_attribute'])
				title_attribute.setCurrentIndex(previous_title_index if previous_title_index > -1 else 0)
				description_attribute.setCurrentIndex(previous_description_index if previous_description_index > -1 else 0)

			selected_only = QCheckBox()
			#checkbox_layout = QVBoxLayout()
			#checkbox_layout.setAlignment(Qt.AlignHCenter)
			#checkbox_layout.addWidget(selected_only)

			label = QLabel(layer_name)
			row_layout.addWidget(label)
			row_layout.addWidget(title_attribute)
			row_layout.addWidget(description_attribute)
			row_layout.addWidget(selected_only)
			#row_layout.addLayout(checkbox_layout)
			row_widget = QWidget()
			row_widget.setObjectName(layer_name)
			row_widget.setLayout(row_layout)
			layout.addWidget(row_widget)

		layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
		self.dialog.drawingLayers.widget().setLayout(layout)

	def show(self):
		vector_layers = [layer for layer in self.plugin.iface.legendInterface().layers() if layer.type() == QgsMapLayer.VectorLayer]
		drawing_layers = self.get_drawing_layers()
		for layer in vector_layers:
			layer_widget = self.dialog.drawingLayers.findChild(QWidget, layer.name())
			is_drawing_layer = layer in drawing_layers
			layer_widget.setVisible(is_drawing_layer)
			if is_drawing_layer and layer.selectedFeatureCount() == 0:
				layer_widget.findChild(QCheckBox).setEnabled(False)

	def get_metadata(self):
		drawing_layers_info = {}
		drawing_layers = self.get_drawing_layers()
		if drawing_layers:
			for layer in drawing_layers:
				layer_widget = self.dialog.drawingLayers.findChild(QWidget, layer.name())
				title_combo = layer_widget.findChild(QComboBox, 'title')
				description_combo = layer_widget.findChild(QComboBox, 'description')
				drawing_layers_info[layer.name()] = {
					'title_attribute': title_combo.itemData(title_combo.currentIndex()),
					'description_attribute': description_combo.itemData(description_combo.currentIndex())
				}
			return {
				'layers_drawing': {
					'filename': self.get_drawing_filename(),
					'layers': drawing_layers_info
				}
			}

	def before_publish(self):
		drawing_layers = self.get_drawing_layers()
		if drawing_layers:
			map_canvas = self.plugin.iface.mapCanvas()
			fields = QgsFields()
			fields.append(QgsField("title", type=QVariant.String))
			fields.append(QgsField("description", type=QVariant.String))
			writer = QgsVectorFileWriter(self.get_drawing_filename(), "utf-8", fields, QGis.WKBUnknown, map_canvas.mapRenderer().destinationCrs(), "GeoJSON")
			for layer in drawing_layers:
				layer_widget = self.dialog.drawingLayers.findChild(QWidget, layer.name())
				title_combo = layer_widget.findChild(QComboBox, 'title')
				description_combo = layer_widget.findChild(QComboBox, 'description')
				title_attribute = title_combo.itemData(title_combo.currentIndex())
				description_attribute = description_combo.itemData(description_combo.currentIndex())
				selected_features_only = layer_widget.findChild(QCheckBox).isChecked()

				transform = None
				if layer.crs() != map_canvas.mapRenderer().destinationCrs():
					transform = QgsCoordinateTransform(layer.crs(), map_canvas.mapRenderer().destinationCrs())
				# QgsVectorLayer.selectedFeaturesIterator is available since 2.6 version, so it is better
				# to convert QgsFeatureIterator to generator and use for loop to iterate features
				if selected_features_only:
					features = layer.selectedFeatures()
				else:
					def features_generator(features_iterator):
						feature = QgsFeature()
						while features_iterator.nextFeature(feature):
							yield feature
					features = features_generator(layer.getFeatures())
				for feature in features:
					f = QgsFeature(fields)
					f.setGeometry(feature.geometry())
					if transform:
						f.geometry().transform(transform)
					f.setAttributes([
						feature.attribute(title_attribute) if title_attribute else '',
						feature.attribute(description_attribute) if description_attribute else ''
					])
					writer.addFeature(f)
