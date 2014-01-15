### Built-in WebGIS application
One of the nice features of GIS.lab is a build-in WebGIS application which is automatically generated for
each user's QGIS project.

Simply save a QGIS project and all file data to '~/Share/<USERNAME>' directory with setting these required configuration:
 * use relative paths (File > Project Properties > General > Save paths). The safest way is to save Your data and project
   file to same directory
 * on-the-fly CRS transformation must be enabled (File > Project Properties > CRS) and target projection
   must be chosen (if You are not sure chose EPSG:3857)
 * OWS advertised extent must be enabled (File > Project Properties > OWS server)
 * for better performance limit number of supported CRSs (File > Project Properties > OWS server > CRS restrictions)

and launch following URL in a web browser:
```
format:
http://web.gis.lab/?PROJECT=<PATH-TO-QGIS-PROJECT-FILE>

* PATH-TO-QGIS-PROJECT-FILE must be relative to '~/Share' directory

example of user 'lab1' who saved 'Central Europe' project file packaged with GIS.lab to ~/Share directory ($ cp -a ~/Repository/data/natural-earth ~/Share/$USER):
http://web.gis.lab/?PROJECT=lab1/natural-earth/central-europe.qgs

```

Additionally, it is possible to configure behavior of WebGIS app via GET parameters in URL.
```
format:
http://web.gis.lab/?PROJECT=<PATH-TO-QGIS-PROJECT-FILE>&<PARAMETER>=<value>&<PARAMETER>=<value>...

```

Supported GET parameters:
 * PROJECT: path to QGIS project file relative to '~/Share' directory. Example: lab1/natural-earth/central-europe.qgs
 * OSM: determines if OpenStreetMap base layer will be added to map. Works only in projection EPSG:3857. Example: true. Default is false.
 * GOOGLE: determines if Google base layer will be added to map. Works only in projection EPSG:3857. Possible values 
 * LAYERS: list of layers to display in map. Example: border,lakes,rivers. Default is auto-detected list of layers from project.
 * VISIBLE: list of layers to set as visible on application start. Example: border. Default: all layers
 * DPI: DPI resolution of map layers. Example: 120. Default: 96. 
 * SCALES: available list of scales of map. Example: 10000,5000,2500. Default: 1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500
 * ZOOM: zoom level to use on start. Example: 2. Default: 0
 * CENTER: coordinates of map center on start. Example: 1234.12,5678.56. Default is center of auto-detected extent from project.
   are: streets, hybrid, satellite, terrain, Example: streets.
 * BALLS: list of balls identifiers containing geometry data in GeoJSON format. Format: <BALL_ID>,<BALL_ID>,...
