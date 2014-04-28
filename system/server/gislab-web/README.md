# GIS.lab Web
## Empty project
To launch empty GIS.lab Web project with OSM and Google base layers open following URL in web
browser:

```
http://web.gis.lab
```

## Existing project
To publish existing project created in QGIS

set following project configurations:

 * use relative paths (Project > Project Properties > General > Save paths). The safest way is to save Your data and project
   file to same directory
 * on-the-fly CRS transformation must be enabled (File > Project Properties > CRS) and target projection
   must be chosen (if You are not sure chose EPSG:3857)

save project to '~/Share/<USERNAME>' directory

and launch following URL in a web browser:
```
format:
http://web.gis.lab/?PROJECT=<PATH-TO-QGIS-PROJECT-FILE>

* PATH-TO-QGIS-PROJECT-FILE must be relative to '~/Share' directory

example of user 'lab1' who saved 'Central Europe' project file packaged with GIS.lab to ~/Share directory ($ cp -a ~/Repository/data/natural-earth ~/Share/$USER):
http://web.gis.lab/?PROJECT=lab1/natural-earth/central-europe.qgs

```

Additionally, it is possible to configure behavior of GIS.lab Web via GET parameters in URL.
```
format:
http://web.gis.lab/?PROJECT=<PATH-TO-QGIS-PROJECT-FILE>&<PARAMETER>=<value>&<PARAMETER>=<value>...

```

### List of parameters:
 * PROJECT: path to QGIS project file relative to '~/Share' directory. Example: lab1/natural-earth/central-europe.qgs

 * BASE: base layers encoded in following syntax: /[<category name>/.../]<layer name>[:<visible (integer)>];<layer name>[:<visible>];/[<category name>/.../]<layer name>[:<visible>];... Example: /cat/subcat/subsubcat/layer1:0;layer2:1;/cat2/subcat2/subsubcat2/layer1:0;layer2:0 Reserved layer names are BLANK, OSM, GROADMAP, GSATELLITE, GHYBRID, GTERRAIN.

 * OVERLAY: overlay layers encoded in following syntax: /[<category name>/.../]<layer name>[:<visible (integer)>:<transparency (integer)>];<layer name>[:<visible>:<transparency>];/[<category name>/.../]<layer name>[:<visible>:<transparency>];... Example: /cat/subcat/subsubcat/layer1:1:50;layer2:1:100;/cat2/subcat2/subsubcat2/layer1:0:75;layer2:1:85

 * SCALES: available list of scales available in map. Example: 10000,5000,2500. Default: 1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500. Some base layers like OSM, GOOGLE or WMS-C can override these values to suite their needs.
 
 * EXTENT: map extent on start. Example 1234.1,5678.5,2345.2,6789.6. Default is extent of the project.
 
 * DRAWINGS: list of drawings identifiers containing geometry data in GeoJSON format. Format: <DRAWING_ID>,<DRAWING_ID>,...


### Parameters usage rules and priorities
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


## Gunicorn deployment
For testing or development, run following command in directory containing 'manage.py' file
```
gunicorn djproject.wsgi:application
```

For production, use this script (update paths to your needs). Use (CPU * 2 + 1) for NUM_WORKERS. If
only one CPU available, use 3 workers.
```
#!/bin/bash

NAME="webgis"
DJANGODIR=/var/www/webgis
SOCKFILE=/var/www/webgis/gunicorn.sock
USER=www-data
GROUP=www-data
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=djproject.settings
DJANGO_WSGI_MODULE=djproject.wsgi
 
cd $DJANGODIR
source /usr/local/python-virtualenvs/webgis/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
 
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
 
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--log-level=debug \
--bind=unix:$SOCKFILE
```


## Credits
 * icons used taken from Heron Mapping Client (http://heron-mc.org/)
 * icons taken from QGIS (http://www.qgis.org)
