# GIS.lab Web

```
http://web.gis.lab
```

## GET parameters:
 * PROJECT: path to QGIS project file relative to '~/Publish' directory. Example: lab1/natural-earth/central-europe.qgs

 * BASE: base layers encoded in following syntax: /[<category name>/.../]<layer name>[:<visible (integer)>];<layer name>[:<visible>];/[<category name>/.../]<layer name>[:<visible>];... Example: /cat/subcat/subsubcat/layer1:0;layer2:1;/cat2/subcat2/subsubcat2/layer1:0;layer2:0 Reserved layer names are BLANK, OSM, GROADMAP, GSATELLITE, GHYBRID, GTERRAIN.

 * OVERLAY: overlay layers encoded in following syntax: /[<category name>/.../]<layer name>[:<visible (integer)>:<transparency (integer)>];<layer name>[:<visible>:<transparency>];/[<category name>/.../]<layer name>[:<visible>:<transparency>];... Example: /cat/subcat/subsubcat/layer1:1:50;layer2:1:100;/cat2/subcat2/subsubcat2/layer1:0:75;layer2:1:85

 * EXTENT: map extent on start. Example 1234.1,5678.5,2345.2,6789.6. Default is extent of the project.

 * DRAWINGS: list of drawings identifiers containing geometry data in GeoJSON format. Format: <DRAWING_ID>,<DRAWING_ID>,...


#### PROJECT
* list of base layers and overlay layers is detected from project.
* visibility of base layers is detected from project. First visible base layer is set as visible if any of base layers is detected as visible OR first base layer is set as visible if all base layers are detected as invisible.
* if no base layer is detected from project BLANK base layer is added and set as visible

#### PROJECT + BASE
* list of base layers is detected from BASE parameter. Visibility of base layers is detected from project and overriden by BASE parameter. First visible base layer is set as visible if any of base layers is detected as visible OR first base layer is set as visible if all base layers are detected as invisible.
* list of overlay layers and their visibility and transparency is detected from project.

#### PROJECT + BASE + OVERLAY
* list of base layers is detected from BASE parameter. Visibility of base layers is detected from project and overriden by BASE parameter. First visible base layer is set as visible if any of base layers is detected as visible OR first base layer is set as visible if all base layers are detected as invisible.
* list of overlay layers and their visibility and transparency is detected from project and overriden by OVERLAY parameter. 


## Credits
 * some icons taken from QGIS (http://www.qgis.org)
