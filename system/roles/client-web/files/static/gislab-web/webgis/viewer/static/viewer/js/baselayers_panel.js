Ext.namespace('WebGIS');
WebgisWmsLayer = OpenLayers.Class(OpenLayers.Layer.WMS, {
	prevResolution: 0,

	moveTo:function(bounds, zoomChanged, dragging) {
		OpenLayers.Layer.WMS.prototype.moveTo.apply(this, arguments);
		// remove back buffer when going into zoom level with resolution outside of layer's minResolution to maxResolution range
		var resolution = this.getResolution();
		if (zoomChanged) {
			if ((resolution < this.minResolution || resolution > this.maxResolution) && (this.prevResolution >= this.minResolution && this.prevResolution <= this.maxResolution)) {
				this.removeBackBuffer();
			}
		}
		this.prevResolution = resolution;
	},

	getURL: function (bounds) {
		var resolution = this.getResolution();
		//console.log('WMS url (resolution:'+resolution+' min:'+this.minResolution+' max:'+this.maxResolution+')');
		if (resolution >= this.minResolution && resolution <= this.maxResolution) {
			return OpenLayers.Layer.WMS.prototype.getURL.apply(this, arguments);
		}
	}
});

WebGIS.BaseLayersPanel = Ext.extend(Ext.tree.TreePanel, {
	baselayerRoot: null,
	selectedLayer: null,

	constructor: function(config) {
		this.map = config.map;
		this.createLayersData(config.baselayers);
		config.root = this.baselayerRoot;
		//config.useArrows = true;
		config.rootVisible = false;
		WebGIS.BaseLayersPanel.superclass.constructor.apply(this, arguments);

		// select visible base layer
		if (!this.selectedLayer) {
			// no visible base layer by default, so find the first suitable in the tree
			this.baselayerRoot.cascade(function(node) {
				if (!this.selectedLayer && node.isLeaf() && node.attributes.layerRecordData.layer) {
					this.selectedLayer = node.attributes.layerRecordData.layer;
					node.attributes.checked = true;
					return false;
				}
			}, this);
		}
		this.setBaseLayer(this.selectedLayer);
	},
	setBaseLayer: function(layer) {
		if (layer.CLASS_NAME == 'OpenLayers.Layer.Google') {
			Ext.Element.select('.olControlScaleLine').addClass("google");
			Ext.Element.select('.olControlAttribution').addClass("google");
		} else if (this.map.baseLayer.CLASS_NAME == 'OpenLayers.Layer.Google') {
			Ext.Element.select('.olControlScaleLine').removeClass("google");
			Ext.Element.select('.olControlAttribution').removeClass("google");
		}
		this.map.setBaseLayer(layer);
		layer.setVisibility(true);
	},
	createLayer: function(layer_config) {
		// create Openlayer Layer
		var attribution = layer_config.attribution;
		if (attribution && attribution.title) {
			if (attribution.url) {
				attribution = String.format('<a href="{0}" target="_blank">{1}</a>', attribution.url, attribution.title);
			} else {
				attribution = attribution.title;
			}
		}
		var layer;
		if (layer_config.type == 'BLANK') {
			layer = new OpenLayers.Layer(
				layer_config.name,
				{
					isBaseLayer: true,
					resolutions: layer_config.resolutions,
					attribution: attribution,
				}
			);
		} else if (layer_config.type == 'OSM') {
			layer = new OpenLayers.Layer.OSM(
				layer_config.name, '', {
					zoomOffset: layer_config.min_zoom_level,
					resolutions: layer_config.resolutions,
					wrapDateLine: false
				}
			);
		} else if (layer_config.type == 'google') {
			var google_map = layer_config.name.slice(1);
			layer = new OpenLayers.Layer.Google(
				layer_config.name,
				{
					type: google.maps.MapTypeId[google_map],
					mapTypeId: google_map,
					minZoomLevel: layer_config.min_zoom_level,
					maxZoomLevel: layer_config.max_zoom_level,
					wrapDateLine: false,
				}
			);
		} else if (layer_config.type == 'WMS') {
			layer = new WebgisWmsLayer(
				layer_config.name,
				[layer_config.url],
				{
					layers: layer_config.wms_layers,
					transparent: false,
					format: layer_config.image_format,
					dpi: layer_config.dpi,
				},
				{
					gutter: 0,
					isBaseLayer: true,
					buffer: 0,
					singleTile: true,
					maxExtent: layer_config.extent,
					displayOutsideMaxExtent: false,
					resolutions: layer_config.resolutions,
					minResolution: layer_config.min_resolution,
					maxResolution: layer_config.max_resolution,
					attribution: attribution,
				}
			);
		} else if (layer_config.type == 'WMSC') {
			layer = new WebgisWmsLayer(
				layer_config.name,
				[layer_config.url],
				{
					layers: layer_config.wms_layers,
					transparent: false,
					format: layer_config.image_format,
					dpi: layer_config.dpi,
					tiled: 'true',
				},
				{
					isBaseLayer: true,
					singleTile: false,
					maxExtent: layer_config.extent,
					displayOutsideMaxExtent: false,
					resolutions: layer_config.resolutions,
					minResolution: layer_config.min_resolution,
					maxResolution: layer_config.max_resolution,
					attribution: attribution,
					tileSize: layer_config.tile_size? new OpenLayers.Size(layer_config.tile_size[0], layer_config.tile_size[1]) : new OpenLayers.Size(256, 256)
				}
			);
		}
		return layer;
	},
	createLayerNode: function(parentNode, layer_config) {
		var node;
		var isGroup = layer_config.hasOwnProperty('layers');
		var title = layer_config.type == 'BLANK'? gettext("Blank") : layer_config.title? layer_config.title : layer_config.name;
		var layerRecordData = {
			title: title,
			name: layer_config.name,
		};
		var visible = (layer_config.visible && !this.selectedLayer) === true;
		if (isGroup) {
			layerRecordData.itemCls = 'layer-category-item';
			node = new Ext.tree.TreeNode({
				text: title,
				leaf: false,
				expanded: true
			});
		} else {
			node = new Ext.tree.TreeNode({
				text: title,
				checked: visible,
				leaf: true,
				expanded: true, // must be set on leaf nodes to make 'beforechildrenrendered' event work
				listeners: {
					beforechildrenrendered: function(node) {
						node.getUI().elNode.setAttribute('depth', node.getDepth());
						if (node.isLeaf()) {
							node.getUI().checkbox.setAttribute('type', 'radio');
							node.getUI().checkbox.setAttribute('name', 'baselayer-radio');
						}
					},
					checkchange: function(node) {
						var layer = node.attributes.layerRecordData.layer;
						this.setBaseLayer(layer);
					}.bind(this),
					click: function(node, evt) {
						if (evt.getTarget().tagName === 'INPUT') {
							node.getUI().checkbox.click();
							node.getUI().toggleCheck(true);
						}
					},
					beforedblclick: function(node, evt) {
						node.getUI().toggleCheck(true);
						return false;
					}
				}
			});
			var layer = this.createLayer(layer_config);
			if (layer) {
				this.map.addLayer(layer);
				layer.setVisibility(visible);
				layerRecordData.layer = layer;
				if (visible) {
					this.selectedLayer = layer;
				}
			} else {
				layerRecordData.itemCls = 'layer-unavailable-item';
			}
		}
		node.attributes.layerRecordData = layerRecordData;
		this.baselayersItems.push(layerRecordData);
		if (isGroup) {
			Ext.each(layer_config.layers, function(child_layer_config) {
				var childNode = this.createLayerNode(node, child_layer_config);
				node.appendChild(childNode);
			}, this);
		}
		return node;
	},
	createLayersData: function(baselayers) {
		this.baselayersItems = [];
		this.baselayerRoot = this.createLayerNode(null, {name: 'Base root', layers: baselayers})
		return baselayers;
	},
	getEncodedLayersParam: function() {
		var encode_layers_set = function(layers_nodes) {
			var n = layers_nodes[0];
			var parents = [];
			while (n.parentNode && n.parentNode != this.baselayerRoot) {
				parents.push(n.parentNode.attributes.layerRecordData.name);
				n = n.parentNode;
			}
			var location = parents.length? '/'+parents.reverse().join('/')+'/' : '/';
			var layers_params = [];
			var selectedBaseLayerName = this.getValue();
			Ext.each(layers_nodes, function(node) {
				var layername = node.attributes.layerRecordData.name;
				var visible = layername == selectedBaseLayerName;
				layers_params.push(String.format('{0}:{1}', layername, visible? 1:0));
			}, this);
			return location+layers_params.join(';');
		}.bind(this);
		var param_parts = [];
		var layers_nodes = [];
		var visit_node = function(node) {
			if (node.isLeaf()) {
				layers_nodes.push(node);
			} else {
				if (layers_nodes.length > 0) {
					param_parts.push(encode_layers_set(layers_nodes));
					layers_nodes = [];
				}
				node.eachChild(visit_node, this);
				if (layers_nodes.length > 0) {
					param_parts.push(encode_layers_set(layers_nodes));
					layers_nodes = [];
				}
			}
		}
		visit_node(this.baselayerRoot);
		return param_parts.join(';');
	}
});
