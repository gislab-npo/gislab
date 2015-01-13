Title: GIS.lab Desktop
Submenu: yes
Order: 20
Slug: gislab-desktop
Status: draft


__GIS.lab Desktop__ is a most powerful client interface. It is designed to be launched from network and it is
running out-of-box on any desktop machine hardware, without any need of installation.

__GIS.lab Desktop__ client can run in two modes - __physical mode__ and __virtual mode__. Both modes are
providing the same environment and features, but are different in deployment and performance.


## Physical client mode
Preferred method of launching __GIS.lab Desktop__ client is a __physical mode__. In this mode, client
machine is configured to start a GIS.lab client environment from network instead of hard disk. Access
to operating system physically installed on client machine is temporary lost and it will be restored
after machine restart without any changes or a danger of data loss. This mode is providing a best
performance.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab physical client]({filename}/images/schema-physical-client.png)  
Fig. 1: Machines turning to GIS.lab Desktop physical clients and back
</div>


## Virtual client mode
In case when user can't offer loosing access to a system physically installed on client machine, there is a possibility
to launch __GIS.lab client__ inside of any Windows, Linux or Mac OS X operating system in __virtual mode__. This mode is
starting the same client environment from network as in physical mode, but it is running inside of VirtualBox virtual
machine. This mode allows to run both systems side-by-side. It is possible use GIS.lab virtual client in a windowed
mode, similar as it would be a common application or in a full screen mode for best user experience.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab virtual client]({filename}/images/schema-virtual-client.png)  
Fig. 2: Machines turning to GIS.lab Desktop virtual clients and back
</div>


# Services provided by GIS.lab client
## Office productivity suite
GIS.lab Desktop environment offers fully featured office productivity suite which contains tools such as _text
documents, tables and presentations editor, Internet browser, Email and chat client, images and vector graphic editor,
video viewer_ and more.

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-office.png)
Fig. 3: LibreOffice Writer
</div>

Implemented by: LibreOffice, Firefox, Thunderbird, Pidgin, GIMP, Inkscape, VLC


## Base maps
Well known base maps such as OpenStreetMap or Google maps are accessible from GIS projects when Internet connection is
available. They are ready to provide a quick overview of any place on earth.

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-osm-base-map.png)
Fig. 4: OpenStreetMap base map in desktop GIS editor
</div>

Implemented by: QGIS, QGIS OpenLayers plugin, GIS.lab Web


## GIS data processing and analysis
GIS software provided by GIS.lab can successfully read and write large number of spatial data formats like _AutoCAD DXF,
ESRI Shapefile, GeoJSON, GML, GeoJPEG, KML, Microstation DGN v.7, OpenStreetMap XML and PBF, SQLite/SpatiaLite,
TIFF/GeoTIFF, PostgreSQL/PostGIS, MS SQL Spatial, Oracle Spatial, OGC WMS and WFS_ and many more. Most of the world's
spatial reference systems (SRS) are transparently handled by on-the-fly reprojection. Geometry and attribute data can be
created and modified by advanced geometry editing, data processing tools and analysis. 

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-analysis.png)
Fig. 5: Available analysis in desktop GIS editor
</div>

Implemented by: QGIS, QIS Processing Toolbox, GDAL, Proj4, SpatiaLite


## Print composer
Powerful print composer allows to create outputs in raster and PDF format. Output maps can include legends, labels,
scale bar, vector shapes and arrows, tables and html content. Output layout can be created as single landscape or
portrait page or as multiple pages in atlas format. 

<div style="text-align:center;padding-top:10px;padding-bottom:10px;" markdown="1">
![GIS.lab client]({filename}/images/client-print-composer.png)
Fig. 6: Print composer
</div>

Implemented by: QGIS, QGIS Print composer
