{% load staticfiles i18n %}

var webgis = angular.module('webgis', []);
webgis.layers = JSON.parse('{{ layers|default:"[]"|escapejs }}');
webgis.baseLayers = JSON.parse('{{ base_layers|default:"[]"|escapejs }}');

goog.provide('ol.control.ButtonControl');
goog.provide('ol.layer.WebgisTmsLayer');
goog.provide('ol.layer.WebgisWmsLayer');
goog.require('ol.control.Control');
goog.require('ol.layer.Tile');
goog.require('ol.layer.Image');

ol.control.ButtonControl = function(opt_options) {

	var options = opt_options || {};

	var anchor = document.createElement('a');
	anchor.href = '#';
	anchor.innerHTML = 'P';

	this.callback = opt_options.callback;
	var this_ = this;
	var onClick = function(e) {
		// prevent #rotate-north anchor from getting appended to the url
		e.preventDefault();
		this_.callback(e);
	};

	anchor.addEventListener('click', onClick, false);
	anchor.addEventListener('touchstart', onClick, false);

	var element = document.createElement('div');
	element.className = goog.isDef(options.className) ? options.className : '';
	element.appendChild(anchor);

	ol.control.Control.call(this, {
		element: element,
		target: options.target
	});
};
ol.inherits(ol.control.ButtonControl, ol.control.Control);


ol.layer.WebgisTmsLayer = function(opt_options) {
	var options = goog.isDef(opt_options) ? opt_options : {};
	goog.base(this,  /** @type {olx.layer.LayerOptions} */ (options));
	this.setLayers(goog.isDef(options.layers) ? options.layers : []);
	this.legendUrl = goog.isDef(options.legendUrl) ? options.legendUrl : '';
	this.project = goog.isDef(options.project) ? options.project : '';
};
goog.inherits(ol.layer.WebgisTmsLayer, ol.layer.Tile);

ol.layer.WebgisTmsLayer.prototype.setLayers = function(layers) {
	var layers_names = [].concat(layers).reverse().join(",");
	this.getSource().layers = layers;
	this.getSource().layersString = layers_names;
	this.getSource().layersHash = CryptoJS.MD5(layers_names).toString();
	this.getSource().tileCache.clear();
	this.changed();
};

ol.layer.WebgisTmsLayer.prototype.getLegendUrls = function(view) {
	var layers_names = this.getSource().layers;
	var base_legend_url = this.legendUrl;
	var tile_grid = this.getSource().getTileGrid();
	var zoom_level = tile_grid.getZForResolution(view.getResolution());
	var base_params = {
		'SERVICE': 'WMS',
		'VERSION': '1.1.1',
		'REQUEST': 'GetLegendGraphic',
		'EXCEPTIONS': 'application/vnd.ogc.se_xml',
		'FORMAT': 'image/png',
		'SYMBOLHEIGHT': '4',
		'SYMBOLWIDTH': '6',
		'LAYERFONTSIZE': '10',
		'LAYERFONTBOLD': 'true',
		'ITEMFONTSIZE': '11',
		'ICONLABELSPACE': '6',
		'SCALE': Math.round(view.getScale()).toString(),
		'PROJECT': this.project,
	}
	var url_template = this.legendUrl + '{hash}/{zoom}.png'.replace('{zoom}', Number(zoom_level).toString());
	url_template = goog.uri.utils.appendParamsFromMap(url_template, base_params);
	var legends_urls = {};
	layers_names.forEach(function (layer_name) {
		var layer_hash = CryptoJS.MD5(layer_name).toString();
		var url = url_template.replace('{hash}', layer_hash);
		url = goog.uri.utils.appendParamsFromMap(url, {'LAYER': layer_name});
		legends_urls[layer_name] = url;
	});
	return legends_urls;
};


ol.layer.WebgisWmsLayer = function(opt_options) {
	var options = goog.isDef(opt_options) ? opt_options : {};
	goog.base(this,  /** @type {olx.layer.LayerOptions} */ (options));
	this.setLayers(goog.isDef(options.layers) ? options.layers : []);
};
goog.inherits(ol.layer.WebgisWmsLayer, ol.layer.Image);
ol.layer.WebgisWmsLayer.prototype.setLayers = function(layers) {
	var layers_names = [].concat(layers).reverse().join(",");
	this.getSource().layers = layers;
	this.getSource().updateParams({LAYERS: layers_names});
};

ol.layer.WebgisWmsLayer.prototype.getLegendUrls = function(view) {
	var layers_names = this.getSource().layers;
	var params = {
		'SERVICE': 'WMS',
		'VERSION': '1.1.1',
		'REQUEST': 'GetLegendGraphic',
		'EXCEPTIONS': 'application/vnd.ogc.se_xml',
		'FORMAT': 'image/png',
		'SYMBOLHEIGHT': '4',
		'SYMBOLWIDTH': '6',
		'LAYERFONTSIZE': '10',
		'LAYERFONTBOLD': 'true',
		'ITEMFONTSIZE': '11',
		'ICONLABELSPACE': '6',
		'SCALE': Math.round(view.getScale()).toString()
	}
	var ows_url = this.getSource().getUrl();
	var legends_urls = {};
	layers_names.forEach(function (layer_name) {
		params['LAYER'] = layer_name;
		var url = goog.uri.utils.appendParamsFromMap(ows_url, params);
		legends_urls[layer_name] = url;
	});
	return legends_urls;
}


ol.Map.prototype.getLayer = function (type) {
	var layer;
	this.getLayers().forEach(function (l) {
		if (type == l.get('type')) {
			layer = l;
		}
	});
	return layer;
}

ol.View.prototype.getScale = function () {
	var resolution = this.getResolution();
	var units = this.getProjection().getUnits();
	var dpi = 25.4 / 0.28;
	var mpu = ol.proj.METERS_PER_UNIT[units];
	var scale = resolution * mpu * 39.37 * dpi;
	return scale;
}


webgis.initMap = function(controls) {
	console.log("initMap");
	// overlay layers
	{% if layers %}
	{% if mapcache_url %}
	var overlays_layer = new ol.layer.WebgisTmsLayer({
		project: '{{ project }}',
		legendUrl: '{{ legend_url }}',
		source: new ol.source.TileImage({
			tileGrid: new ol.tilegrid.TileGrid ({
				origin: ol.extent.getBottomLeft({{ project_extent }}),
				resolutions: {{ tile_resolutions }},
				tileSize: 256
			}),
			tileUrlFunction: function(tileCoord, pixelRatio, projection) {
				var z = tileCoord[0];
				var x = tileCoord[1];
				var y = tileCoord[2];
				var template = "{{ mapcache_url }}{hash}/{z}/{x}/{y}.png?PROJECT={{ project }}&LAYERS={layers}";
				var url = template
					.replace('{hash}', this.layersHash)
					.replace('{z}', z.toString())
					.replace('{x}', x.toString())
					.replace('{y}', y.toString())
					.replace('{layers}', this.layersString);
				return url;
			},
			//tilePixelRatio: 1.325
		}),
		{% else %}
	var overlays_layer = new ol.layer.WebgisWmsLayer({
		source: new ol.source.ImageWMS({
			url: "{{ ows_url }}",
			params: {
				'PROJECT': '{{ project }}',
				'FORMAT': 'image/png',
			},
			serverType: ol.source.wms.ServerType.QGIS
		}),
		{% endif %}
		//layers: ['Roads'],
		extent: {{ project_extent }},
	});
	overlays_layer.set("type", "qgislayer");
	{% endif %}

	var base_layer = new ol.layer.Tile({
		source: new ol.source.OSM(),
		extent: {{ project_extent }},
	});
	
	console.log(webgis.baseLayers);
	var layer_data = webgis.baseLayers[0];
	if (layer_data && layer_data.url) {
		var base_wms_layer = new ol.layer.Image({
			source: new ol.source.ImageWMS({
				url: layer_data.url,
				resolutions: layer_data.resolutions,
				params: {
					'LAYERS': layer_data.wms_layers.join(','),
					'FORMAT': layer_data.format,
					'TRANSPARENT': 'false'
				},
				serverType: ol.source.wms.ServerType.MAPSERVER
			}),
			extent: layer_data.extent
		});
	}

	base_layer.set("type", "baselayer");
	if (!controls) {
		controls = [];
	}
	var map = new ol.Map({
		target: 'map',
		layers: [
			base_layer,
			//base_wms_layer,
			overlays_layer
		],
		view: new ol.View({
			projection: new ol.proj.Projection({
				code: "{{ projection.code }}",
				units: "{{ units }}",
				extent: {{ project_extent }},
			}),
			resolutions: {{ tile_resolutions }},
			extent: {{ project_extent }},
		}),
		controls: ol.control.defaults({
			attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
				collapsible: false
			})
		}).extend(controls),
		renderer: ol.RendererType.CANVAS
	});
	map.getView().fitExtent({{ zoom_extent}}, map.getSize());
	return map;
}; // end of main function

