# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GIS.lab Web plugin
 Publish your projects into GIS.lab Web application
 ***************************************************************************/
"""

# Import the PyQt and QGIS libraries
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *


def _save_topic(dialog, topic_item):
	visible_overlays = []
	def collect_visible_overlays(widget):
		if widget.data(0, Qt.UserRole):
			#if not widget.isHidden() and widget.checkState(0) == Qt.Checked:
			if not widget.isDisabled() and widget.checkState(0) == Qt.Checked:
				visible_overlays.append(widget.text(0))
		else:
			for index in range(widget.childCount()):
				collect_visible_overlays(widget.child(index))
	collect_visible_overlays(dialog.topicLayers.invisibleRootItem())
	topic_item.setData(Qt.UserRole, {
		'abstract': dialog.topicAbstract.toPlainText(),
		'visible_overlays': visible_overlays
	})

def update_topics_layers(dialog):
	# hide excluded layer items (it must be done after attaching of all widgets to the QTreeWidget)
	def hide_excluded_layers(group_item):
		for row in range(group_item.rowCount()):
			item = group_item.child(row, 0)
			if item.rowCount() > 0:
				hide_excluded_layers(item)
			else:
				is_exported_as_vector = group_item.child(row, 1).checkState() == Qt.Checked
				is_hidden = group_item.child(row, 3).checkState() == Qt.Checked
				if item.checkState() == Qt.Unchecked or is_exported_as_vector or is_hidden:
					for topic_layer_item in dialog.topicLayers.findItems(item.text(), Qt.MatchExactly | Qt.MatchRecursive):
						if is_hidden:
							topic_layer_item.setDisabled(True)
						else:
							topic_layer_item.setHidden(True)
	def update_available_layers(widget):
		for index in range(widget.childCount()):
			child_widget = widget.child(index)
			if child_widget.childCount() > 0:
				update_available_layers(child_widget)
				group_empty = True
				for child_index in range(child_widget.childCount()):
					if not child_widget.child(child_index).isHidden():
						group_empty = False
						break
				child_widget.setHidden(group_empty)
			else:
				layers_model = dialog.treeView.model()
				layer_item = layers_model.findItems(child_widget.text(0), Qt.MatchExactly | Qt.MatchRecursive)[0]
				is_layer_visible = layer_item.checkState() == Qt.Unchecked
				is_exported_as_vector = layers_model.columnItem(layer_item, 1).checkState() == Qt.Checked
				is_hidden = layers_model.columnItem(layer_item, 3).checkState() == Qt.Checked
				child_widget.setHidden(is_exported_as_vector or is_layer_visible)
				child_widget.setDisabled(is_hidden)
	update_available_layers(dialog.topicLayers.invisibleRootItem())

def setup_topics_ui(dialog, overlay_layers_tree):
	def add_topic():
		item = QListWidgetItem("New topic")
		item.setFlags(item.flags() | Qt.ItemIsEditable)
		dialog.topicsList.addItem(item)
		dialog.topicsList.editItem(item)
		dialog.topicsList.setCurrentRow(dialog.topicsList.count()-1)

	def remove_topic():
		dialog.topicsList.takeItem(dialog.topicsList.row(dialog.topicsList.selectedItems()[0]))

	dialog.addTopic.released.connect(add_topic)
	dialog.removeTopic.released.connect(remove_topic)

	def copy_tree_widget(group_item):
		new_widget = QTreeWidgetItem()
		new_widget.setText(0, group_item.text())
		for row in range(group_item.rowCount()):
			item = group_item.child(row, 0)
			if item.rowCount() > 0:
				layer_widget = copy_tree_widget(item)
			else:
				layer_widget = QTreeWidgetItem()
				layer_widget.setText(0, item.text())
				layer_widget.setData(0, Qt.UserRole, item.data(Qt.UserRole))
			layer_widget.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
			layer_widget.setCheckState(0, Qt.Checked)
			new_widget.addChild(layer_widget)
		return new_widget

	dialog.topicLayers.addTopLevelItems(copy_tree_widget(dialog.treeView.model().invisibleRootItem()).takeChildren())
	update_topics_layers(dialog)

	dialog.topicWidget.setEnabled(False)

	def topic_changed(current, previous):
		if previous is None:
			dialog.topicWidget.setEnabled(True)
		else:
			_save_topic(dialog, previous)
		if current:
			# load topic data to UI
			current_data = current.data(Qt.UserRole) or {}
			dialog.topicAbstract.setPlainText(current_data.get('abstract', ''))
			visible_overlays = current_data.get('visible_overlays')
			def set_visible_overlays(widget):
				if widget.data(0, Qt.UserRole):
					if not widget.isDisabled():
						if visible_overlays:
							widget.setCheckState(0, Qt.Checked if widget.text(0) in visible_overlays else Qt.Unchecked)
						else:
							widget.setCheckState(0, Qt.Checked)
				else:
					for index in range(widget.childCount()):
						set_visible_overlays(widget.child(index))
			set_visible_overlays(dialog.topicLayers.invisibleRootItem())

	dialog.topicsList.currentItemChanged.connect(topic_changed)

def load_topics_from_metadata(dialog, metadata):
	"""load topics from previous version of published project"""
	for topic_data in metadata.get('topics') or []:
		item = QListWidgetItem(topic_data.pop('title'))
		item.setFlags(item.flags() | Qt.ItemIsEditable)
		item.setData(Qt.UserRole, topic_data)
		dialog.topicsList.addItem(item)
	dialog.topicsList.setCurrentRow(0)

def get_topics(dialog):
	"""Returns list of topics data (title, abstract, visible layers)"""
	if dialog.topicsList.selectedItems():
		_save_topic(dialog, dialog.topicsList.selectedItems()[0])
	topics = []
	for index in range(dialog.topicsList.count()):
		item = dialog.topicsList.item(index)
		topic_data = dict(item.data(Qt.UserRole))
		topic_data['title'] = item.text()
		topics.append(topic_data)
	return topics
