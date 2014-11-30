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
from summary import CSS_STYLE


GISLAB_WEB_URL = 'https://web.gis.lab'


class ConfirmationPage(PublishPage):

	def __init__(self, plugin, page, metadata=None):
		super(ConfirmationPage, self).__init__(plugin, page, metadata=None)
		page.setButtonText(QWizard.CancelButton, "Close")
		#page.setButtonText(QWizard.FinishButton, "Ok")

	def show(self):
		datasources = []
		if self.plugin.metadata.get('vector_layers'):
			datasources.append(os.path.join(os.path.dirname(self.plugin.project.fileName()), self.plugin.metadata['vector_layers']['filename']))
		def collect_layers_datasources(layer_node):
			for index in range(layer_node.rowCount()):
				collect_layers_datasources(layer_node.child(index))
			layer = layer_node.data(Qt.UserRole)
			if layer and layer_node.checkState() == Qt.Checked:
				layer_datasource = layer.source()
				if layer_datasource not in datasources:
					datasources.append(layer_datasource)
		collect_layers_datasources(self.dialog.treeView.model().invisibleRootItem())

		html = u"""<html>
			<head>{0}</head>
			<body>
				<p><h4>Project '{1}' was successfully published.</h4></p>
				<p>Copy all project files to '~/Publish/{5}' folder on GIS.lab server and visit GIS.lab User page <a href="{6}/user">{6}/user</a> to launch this project in GIS.lab Web.</p>

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
				self.plugin.metadata['title'],
				self.plugin.project.fileName(),
				os.path.splitext(self.plugin.project.fileName())[0] + '.meta',
				''.join(['<li>{0}</li>'.format(datasource) for datasource in datasources]),
				os.environ['USER'],
				GISLAB_WEB_URL
		)
		self.dialog.confirmation_info.setHtml(html)
