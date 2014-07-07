Title: GIS.lab client
Submenu: yes
Order: 20
Slug: gislab-client


__GIS.lab client__ combines best features of web application like central software distribution with capabilities and performance of desktop computer. 

GIS.lab client can run in two modes - __physical client mode__ and __virtual client mode__. Both provide the same environment and features, but differ in deployment and performance.


## Physical client mode
Preferred method of launching __GIS.lab client__ machine is a __physical client mode__. In this mode, client machine is configured to boot a GIS.lab client environment from network boot service running on GIS.lab server. This configuration is done in BIOS or by pressing F12 key early in boot process. Access to operating system physically installed on client machine is temporary not available (it will be restored after restart without any changes or a danger of data loss). This mode provides best performance.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab physical client]({filename}/images/schema-physical-client.png)  
Fig. 2: Empty machine or machine running Windows turning to GIS.lab physical client and back
</div>


## Virtual client mode
In case when user can't offer loosing access to a system physically installed on client machine, there is a possibility to launch __GIS.lab client__ inside of any Windows, Linux or Mac OS X operating system in __virtual client mode__. This mode starts the same client environment from network boot service as in physical mode, but it runs inside of VirtualBox virtual machine. This mode allows to run both systems side-by-side. It is possible use GIS.lab virtual client in a windowed mode, similar as it would be a common application or in a full screen mode for best user experience.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab virtual client]({filename}/images/schema-virtual-client.png)  
Fig. 3: Machine running Windows launching GIS.lab virtual client
</div>

In a both modes, client machine runs fully featured operating system capable to use client's hardware potential to minimize server load.


## Third party clients
Any third-party computers can be connected to GIS.lab network without requirement to launch GIS.lab client environment (in physical or virtual mode). After network configuration is automatically received from GIS.lab server (DHCP), third-party computer can use some limited set of services provided by GIS.lab network like Internet sharing, file sharing, geo-database, OWS services and GIS.lab Web. 


# Services provided by GIS.lab client
## Office productivity suite
GIS.lab client environment offers fully featured office productivity suite which contains tools such as _text documents, tables and presentations editor, Internet browser, Email and chat client, images and vector graphic editor and video viewer_ and more.

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-office.png)
Fig. 1: LibreOffice Writer
</div>

Implemented by: LibreOffice, Firefox, Thunderbird, Pidgin, GIMP, Inkscape, VLC


## Base maps
Well known base maps such as OpenStreetMap or Google maps are accessible from GIS projects when Internet connection is available. They are ready to provide a quick overview of any place on earth.

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-osm-base-map.png)
Fig. 2: OpenStreetMap base map in desktop GIS editor
</div>

Implemented by: QGIS, QGIS OpenLayers plugin, GIS.lab Web


## GIS data processing and analysis
GIS software provided by GIS.lab can successfully read and write large number of spatial data formats like _AutoCAD DXF, ESRI Shapefile, GeoJSON, GML, GeoJPEG, KML, Microstation DGN v.7, OpenStreetMap XML and PBF, SQLite/SpatiaLite, TIFF/GeoTIFF, PostgreSQL/PostGIS, MS SQL Spatial, Oracle Spatial, OGC WMS and WFS_ and many more. Most of the world's spatial reference systems (SRS) are transparently handled by on-the-fly reprojection. Geometry and attribute data can be created and modified by advanced geometry editing, data processing tools and analysis. 

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-analysis.png)
Fig. 3: Available analysis in desktop GIS editor
</div>

Implemented by: QGIS, QIS Processing Toolbox, GDAL, Proj4, SpatiaLite


## Print composer
Powerful print composer allows to create outputs in raster and PDF format. Output maps can include legends, labels, scale bar, vector shapes and arrows, tables and html content. Output layout can be created as single landscape or portrait page or as multiple pages in atlas format. 

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-print-composer.png)
Fig. 4: Print composer
</div>

Implemented by: QGIS, QGIS Print composer
