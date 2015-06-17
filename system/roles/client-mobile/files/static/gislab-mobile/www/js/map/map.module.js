angular.module('gl.map', []);

goog.require('ol.source.TileImage');
goog.require('ol.source.ImageWMS');
goog.provide('ol.source.WebgisTileImage');
goog.provide('ol.source.WebgisImageWMS');


ol.source.WebgisTileImage = function(opt_options) {
	var options = goog.isDef(opt_options) ? opt_options : {};
	goog.base(this,  /** @type {olx.layer.LayerOptions} */ (options));
	this.layers = (goog.isDef(options.layers) ? options.layers : []);
	this.tilesUrl = goog.isDef(options.tilesUrl) ? options.tilesUrl : '';
	this.project = goog.isDef(options.project) ? options.project : '';
	this.layersAttributions = goog.isDef(options.layersAttributions) ? options.layersAttributions : {};
	this.layersOrder = goog.isDef(options.layersOrder) ? options.layersOrder : {};
	this.tileUrlFunction = this._tileUrlFunction;

	// create legend url tempalte
	if (goog.isDef(options.legendUrl)) {
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
			'PROJECT': this.project,
		}
		this.legendUrlTemplate = options.legendUrl + '{hash}/{zoom}.png';
		this.legendUrlTemplate = goog.uri.utils.appendParamsFromMap(this.legendUrlTemplate, base_params);
	}
	this.setVisibleLayers(goog.isDef(options.visibleLayers) ? options.visibleLayers : []);
};
goog.inherits(ol.source.WebgisTileImage, ol.source.TileImage);

ol.source.WebgisTileImage.prototype._tileUrlFunction = function(tileCoord, pixelRatio, projection) {
	var z = tileCoord[0];
	var x = tileCoord[1];
	var y = tileCoord[2];
	var url = this.tileUrlTemplate
		.replace('{z}', z.toString())
		.replace('{x}', x.toString())
		.replace('{y}', y.toString());
	return url;
};

ol.source.WebgisTileImage.prototype.setVisibleLayers = function(layers) {
	var ordered_layers = [].concat(layers);
	ordered_layers.sort(function(l1, l2) {
		return this.layersOrder[l2]-this.layersOrder[l1];
	}.bind(this));
	this.visibleLayers = ordered_layers;
	var layers_names = ordered_layers.join(",");
	this.tileUrlTemplate = "{mapcache_url}{hash}/{z}/{x}/{y}.png?PROJECT={project}&LAYERS={layers}"
			.replace('{mapcache_url}', this.tilesUrl)
			.replace('{hash}', CryptoJS.MD5(layers_names).toString())
			.replace('{project}', this.project)
			.replace('{layers}', layers_names);
	this.tileCache.clear();

	// update attributions
	if (this.layersAttributions) {
		var attributions = [];
		var attributions_html = [];
		ordered_layers.forEach(function(layername) {
			var attribution = this.layersAttributions[layername];
			if (attribution && attributions_html.indexOf(attribution.getHTML()) == -1) {
				attributions.push(attribution);
				attributions_html.push(attribution.getHTML());
			}
		}, this);
		this.setAttributions(attributions);
	}
	this.changed();
};

ol.source.WebgisTileImage.prototype.getVisibleLayers = function() {
	return this.visibleLayers;
};

ol.source.WebgisTileImage.prototype.getLegendUrl = function(layername, view) {
	var tile_grid = this.getTileGrid();
	var zoom_level = tile_grid.getZForResolution(view.getResolution());
	var legendUrl = this.legendUrlTemplate
		.replace('{hash}', CryptoJS.MD5(layername).toString())
		.replace('{zoom}', Number(zoom_level).toString());
	legendUrl = goog.uri.utils.appendParamsFromMap(legendUrl, {
		'LAYER': layername,
		'SCALE': Math.round(view.getScale()).toString()
	});
	return legendUrl;
};


ol.source.WebgisImageWMS = function(opt_options) {
	var options = goog.isDef(opt_options) ? opt_options : {};
	goog.base(this,  /** @type {olx.layer.LayerOptions} */ (options));
	this.layersAttributions = goog.isDef(options.layersAttributions) ? options.layersAttributions : {};
	this.layersOrder = goog.isDef(options.layersOrder) ? options.layersOrder : {};
	var legendUrlParams = {
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
	}
	this.legendUrlTemplate = goog.uri.utils.appendParamsFromMap(options.url, legendUrlParams);
	this.setVisibleLayers(goog.isDef(options.visibleLayers) ? options.visibleLayers : []);
};
goog.inherits(ol.source.WebgisImageWMS, ol.source.ImageWMS);

ol.source.WebgisImageWMS.prototype.setVisibleLayers = function(layers) {
	var ordered_layers = [].concat(layers);
	ordered_layers.sort(function(l2, l1) {
		return this.layersOrder[l1]-this.layersOrder[l2];
	}.bind(this));
	// update attributions
	if (this.layersAttributions) {
		var attributions = [];
		var attributions_html = [];
		ordered_layers.forEach(function(layername) {
			var attribution = this.layersAttributions[layername];
			if (attribution && attributions_html.indexOf(attribution.getHTML()) == -1) {
				attributions.push(attribution);
				attributions_html.push(attribution.getHTML());
			}
		}, this);
		this.setAttributions(attributions);
	}
	this.updateParams({LAYERS: ordered_layers.join(",")});
	this.visibleLayers = ordered_layers;
};

ol.source.WebgisImageWMS.prototype.getVisibleLayers = function() {
	return this.visibleLayers;
};

ol.source.WebgisImageWMS.prototype.getLegendUrl = function(layername, view) {
	var legendUrl = goog.uri.utils.appendParamsFromMap(this.legendUrlTemplate, {
		LAYER: layername,
		SCALE: Math.round(view.getScale()).toString()
	});
	return legendUrl;
};


ol.Map.prototype.getLayer = function (name) {
	var layer;
	this.getLayers().forEach(function (l) {
		if (name == l.get('name')) {
			layer = l;
		}
	});
	return layer;
};

ol.View.prototype.getScale = function () {
	var resolution = this.getResolution();
	var units = this.getProjection().getUnits();
	var dpi = 25.4 / 0.28;
	var mpu = ol.proj.METERS_PER_UNIT[units];
	var scale = resolution * mpu * 39.37 * dpi;
	return scale;
};

ol.Map.prototype.getControlByClass = function (clazz) {
	var control;
	this.getControls().getArray().some(function (ctrl) {
		if (ctrl instanceof clazz) {
			control = ctrl;
			return true;
		}
	});
	return control;
};
