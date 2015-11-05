Build
=====

npm install
gulp lint
gulp default
gulp uglify

-----
$ npm install openlayers

$ cp ol3/webgis.map.js node_modules/openlayers/src/ol/
$ cp ol3/externs/webgis.js node_modules/openlayers/externs/
$ cp ol3/webgis.json node_modules/openlayers/build/
($ cp ol3/webgis-debug.json node_modules/openlayers/build/)
$ cd node_modules/openlayers

$ node tasks/build.js build/webgis.json build/ol.min.js
$ cp build/ol.min.js ../../../webgis/ol3_viewer/static/core/lib/
$ cp dist/ol.css ../../../webgis/ol3_viewer/static/core/lib/

$ node tasks/build.js build/webgis-debug.json build/ol.debug.js
$ cp build/ol.debug.js ../../../webgis/ol3_viewer/static/core/lib/

Note: After some changes in API, delete file build/info.json and compile it twice
