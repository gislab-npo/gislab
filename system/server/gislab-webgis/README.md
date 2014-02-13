### Built-in WebGIS application

#### Empty project
To launch empty WebGIS project with OSM and Google base layers open following URL in web
browser. 

```
http://web.gis.lab
```

#### Existing project
To publish existing project created in QGIS

set following project configurations:

 * use relative paths (Project > Project Properties > General > Save paths). The safest way is to save Your data and project
   file to same directory
 * on-the-fly CRS transformation must be enabled (File > Project Properties > CRS) and target projection
   must be chosen (if You are not sure chose EPSG:3857)
 * OWS advertised extent must be enabled (File > Project Properties > OWS server)
 * for better performance limit number of supported CRSs (File > Project Properties > OWS server > CRS restrictions)

save project to '~/Share/<USERNAME>' directory

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
   are: streets, hybrid, satellite, terrain, Example: streets.
 * LAYERS: list of layers to display in map. Example: border,lakes,rivers. Default is auto-detected list of layers from project.
 * VISIBLE: list of layers to set as visible on application start. Example: border. Default: all layers
 * DPI: DPI resolution of map layers. Example: 120. Default: 96. 
 * SCALES: available list of scales of map. Example: 10000,5000,2500. Default: 1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500
 * EXTENT: desired extent of the map on start. Example 1234.1,5678.5,2345.2,6789.6. Default is extent of the project.
 * DRAWINGS: list of drawings identifiers containing geometry data in GeoJSON format. Format: <DRAWING_ID>,<DRAWING_ID>,...


#### Credits
 * icons used taken from Heron Mapping Client (http://heron-mc.org/)
 * icons taken from QGIS (http://www.qgis.org)
