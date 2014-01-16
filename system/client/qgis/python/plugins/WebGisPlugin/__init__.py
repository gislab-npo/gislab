# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WebGisPlugin
                                 A QGIS plugin
 Publish your projects into WebGis application
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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load WebGisPlugin class from file WebGisPlugin
    from webgisplugin import WebGisPlugin
    return WebGisPlugin(iface)
