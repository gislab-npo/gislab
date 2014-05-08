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

WebGIS.BaseLayersComboBox = Ext.extend(Ext.form.ComboBox, {
	baselayerRoot: null,
	selectedLayerRecordData: null,

	constructor: function(config) {
		this.map = config.map;
		// create base layers tree for easier generating of encoded base layers parameter
		// and items for combobox store
		this.createLayersData(config.baselayers);
		config.store = new Ext.data.JsonStore({
			data: { baselayers: this.baselayersItems },
			storeId: 'baselayers-store',
			root: 'baselayers',
			fields: [{
					name: 'name',
					type: 'string'
				}, {
					name: 'title',
					type: 'string'
				}, {
					name: 'itemCls',
					type: 'string'
				}, {
					name: 'indent',
					type: 'intege'
				}
			]
		});
		config.displayField = 'title';
		config.valueField = 'name';
		config.mode = 'local';
		config.triggerAction = 'all';
		config.forceSelection = true;
		config.tpl = '<tpl for="."><div class="x-combo-list-item {itemCls} list-item-indent-{indent}">{title}</div></tpl>';
		WebGIS.BaseLayersComboBox.superclass.constructor.apply(this, arguments);
		// select visible base layer
		if (!this.selectedLayerRecordData) {
			// no visible base layer by default, so find the first suitable in the tree
			this.baselayerRoot.cascade(function(node) {
				if (!this.selectedLayerRecordData && node.isLeaf() && node.attributes.layerRecordData.layer) {
					this.selectedLayerRecordData = node.attributes.layerRecordData;
					return false;
				}
			}, this);
		}
		if (this.selectedLayerRecordData) {
			this.setValue(this.selectedLayerRecordData.title);
			this.selectedLayerRecordData.layer.setVisibility(true);
			this.map.setBaseLayer(this.selectedLayerRecordData.layer);
		}
	},
	listeners: {
		beforeselect: function(combo, record, index) {
			return !(record.get('itemCls') == 'layer-category-item' || record.get('itemCls') == 'layer-unavailable-item');
		},
		select: function (combo, record, index) {
			var layer = record.json.layer;
			this.map.setBaseLayer(layer);
		}
	},
	createLayer: function(layer_config) {
		// create Openlayer Layer
		var attribution = layer_config.attribution;
		if (attribution && attribution.title) {
			if (attribution.url) {
				attribution = String.format('<a href="{0}">{1}</a>', attribution.url, attribution.title);
			} else {
				attribution = attribution.title;
			}
		}
		var layer;
		if (layer_config.type == 'BLANK') {
			layer = new OpenLayers.Layer(
				"Blank",
				{
					isBaseLayer: true,
					resolutions: layer_config.resolutions,
					attribution: attribution,
				}
			);
		} else if (layer_config.type == 'OSM') {
			layer = new OpenLayers.Layer.OSM();
		} else if (layer_config.type == 'google') {
			var google_map = layer_config.name.slice(1);
			layer = new OpenLayers.Layer.Google(
				layer_config.name,
				{
					type: google.maps.MapTypeId[google_map],
					mapTypeId: google_map,
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
					tiled: 'true', // TODO maybe for TileGo only?
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
				}
			);
		}
		return layer;
	},
	createLayerNode: function(parentNode, layer_config) {
		var node;
		var isGroup = layer_config.hasOwnProperty('layers');
		var layerRecordData = {
			title: layer_config.title? layer_config.title : layer_config.name,
			name: layer_config.name,
			indent: parentNode.attributes.layerRecordData? parentNode.attributes.layerRecordData.indent+1 : 0,
		};
		if (isGroup) {
			layerRecordData.itemCls = 'layer-category-item';
			node = new Ext.tree.TreeNode({leaf: false});
		} else {
			node = new Ext.tree.TreeNode({leaf: true});
			var layer = this.createLayer(layer_config);
			if (layer) {
				var visible = layer_config.visible && !this.selectedLayerRecordData;
				if (visible) {
					this.selectedLayerRecordData = layerRecordData;
				}
				this.map.addLayer(layer);
				layer.setVisibility(visible);
				layerRecordData.layer = layer;
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
		this.baselayerRoot = new Ext.tree.TreeNode({});
		Ext.each(baselayers, function(layer_config) {
			var node = this.createLayerNode(this.baselayerRoot, layer_config);
			this.baselayerRoot.appendChild(node);
		}, this);
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
