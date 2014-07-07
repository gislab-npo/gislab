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


def _save_theme(dialog, theme_item):
	visible_overlays = []
	def collect_visible_overlays(widget):
		if widget.data(0, Qt.UserRole):
			if not widget.isHidden() and widget.checkState(0) == Qt.Checked:
				visible_overlays.append(widget.text(0))
		else:
			for index in range(widget.childCount()):
				collect_visible_overlays(widget.child(index))
	collect_visible_overlays(dialog.themeLayers.invisibleRootItem())
	theme_item.setData(Qt.UserRole, {
		'abstract': dialog.themeAbstract.toPlainText(),
		'visible_overlays': visible_overlays
	})

def setup_themes_ui(dialog, overlay_layers_tree):
	def add_theme():
		item = QListWidgetItem("New Theme")
		item.setFlags(item.flags() | Qt.ItemIsEditable)
		dialog.themesList.addItem(item)
		dialog.themesList.editItem(item)
		dialog.themesList.setCurrentRow(dialog.themesList.count()-1)

	def remove_theme():
		dialog.themesList.takeItem(dialog.themesList.row(dialog.themesList.selectedItems()[0]))

	dialog.addTheme.released.connect(add_theme)
	dialog.removeTheme.released.connect(remove_theme)

	def copy_tree_widget(widget):
		new_widget = QTreeWidgetItem()
		new_widget.setText(0, widget.text(0))
		new_widget.setData(0, Qt.UserRole, widget.data(0, Qt.UserRole))
		new_widget.setFlags(widget.flags())
		is_hidden = widget.checkState(1) == Qt.Checked
		if is_hidden:
			new_widget.setDisabled(True)
		for index in range(widget.childCount()):
			child = widget.child(index)
			new_widget.addChild(copy_tree_widget(child))
		new_widget.setCheckState(0, Qt.Checked)
		return new_widget

	dialog.themeLayers.addTopLevelItems(copy_tree_widget(dialog.overlaysTree.invisibleRootItem()).takeChildren())

	# hide excluded layer items, must be done after attaching of all widgets to the QTreeWidget
	def hide_excluded_layers(widget):
		for index in range(widget.childCount()):
			hide_excluded_layers(widget.child(index))
		if widget.checkState(0) == Qt.Unchecked:
			for theme_layer_item in dialog.themeLayers.findItems(widget.text(0), Qt.MatchExactly | Qt.MatchRecursive):
				theme_layer_item.setHidden(True)
	hide_excluded_layers(dialog.overlaysTree.invisibleRootItem())

	# setup synchronization of available and hidden layers in themes with with main layers tree widget
	def itemchanged(item, column):
		# layer visibility changed
		theme_layer_item = dialog.themeLayers.findItems(item.text(0), Qt.MatchExactly | Qt.MatchRecursive)[0]
		if column == 0:
			theme_layer_item.setHidden(item.checkState(0) == Qt.Unchecked)
			# this helps to avoid empty layers group to be visible in themes
			if item.parent() and item.parent().checkState(0) == Qt.Unchecked:
				theme_layer_item.parent().setHidden(True)
		elif column == 1:
			is_hidden = item.checkState(1) == Qt.Checked
			theme_layer_item.setDisabled(is_hidden)

	dialog.overlaysTree.itemChanged.connect(itemchanged)

	dialog.themeWidget.setEnabled(False)

	def theme_changed(current, previous):
		if previous is None:
			dialog.themeWidget.setEnabled(True)
		else:
			_save_theme(dialog, previous)
		if current:
			# load theme data to UI
			current_data = current.data(Qt.UserRole) or {}
			dialog.themeAbstract.setPlainText(current_data.get('abstract', ''))
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
			set_visible_overlays(dialog.themeLayers.invisibleRootItem())

	dialog.themesList.currentItemChanged.connect(theme_changed)

def load_themes_from_metadata(dialog, metadata):
	"""load themes from previous version of published project"""
	for theme_data in metadata.get('themes') or []:
		item = QListWidgetItem(theme_data.pop('title'))
		item.setFlags(item.flags() | Qt.ItemIsEditable)
		item.setData(Qt.UserRole, theme_data)
		dialog.themesList.addItem(item)
	dialog.themesList.setCurrentRow(0)

def get_themes(dialog):
	"""Returns list of themes data (title, abstract, visible layers)"""
	if dialog.themesList.selectedItems():
		_save_theme(dialog, dialog.themesList.selectedItems()[0])
	themes = []
	for index in range(dialog.themesList.count()):
		item = dialog.themesList.item(index)
		theme_data = dict(item.data(Qt.UserRole))
		theme_data['title'] = item.text()
		themes.append(theme_data)
	return themes
