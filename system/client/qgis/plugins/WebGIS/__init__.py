# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WebGIS plugin
 Publish your projects into WebGis application
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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
	from webgisplugin import WebGisPlugin
	return WebGisPlugin(iface)
