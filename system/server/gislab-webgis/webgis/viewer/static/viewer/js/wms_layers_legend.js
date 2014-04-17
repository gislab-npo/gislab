/*
  List of customizations of GeoExt.WMSLegend:
   * sets default FORMAT parameter in GetLegendGraphic requests only if needed
   * loading layers in reverse order as defined in OpenLayers.Layer.params.LAYERS property
   * keeps layers order when changing layers visibility
*/

Ext.override(GeoExt.WMSLegend, {
	/** private: method[getLegendUrl]
	 *  :param layerName: ``String`` A sublayer.
	 *  :param layerNames: ``Array(String)`` The array of sublayers,
	 *	  read from this.layerRecord if not provided.
	 *  :return: ``String`` The legend URL.
	 *
	 *  Get the legend URL of a sublayer.
	 */
	getLegendUrl: function(layerName, layerNames) {
		var rec = this.layerRecord;
		var url;
		var styles = rec && rec.get("styles");
		var layer = rec.getLayer();
		layerNames = layerNames || [layer.params.LAYERS].join(",").split(",");

		var styleNames = layer.params.STYLES &&
							 [layer.params.STYLES].join(",").split(",");
		var idx = layerNames.indexOf(layerName);
		var styleName = styleNames && styleNames[idx];
		// check if we have a legend URL in the record's
		// "styles" data field
		if(styles && styles.length > 0) {
			if(styleName) {
				Ext.each(styles, function(s) {
					url = (s.name == styleName && s.legend) && s.legend.href;
					return !url;
				});
			} else if(this.defaultStyleIsFirst === true && !styleNames &&
					  !layer.params.SLD && !layer.params.SLD_BODY) {
				url = styles[0].legend && styles[0].legend.href;
			}
		}
		
		if(!url) {
			url = layer.getFullRequestString({
				REQUEST: "GetLegendGraphic",
				WIDTH: null,
				HEIGHT: null,
				EXCEPTIONS: "application/vnd.ogc.se_xml",
				LAYER: layerName,
				LAYERS: null,
				STYLE: (styleName !== '') ? styleName: null,
				STYLES: null,
				SRS: null,
				FORMAT: null,
				TIME: null
			});
		}
		var params = Ext.apply({}, this.baseParams);
		if (layer.params._OLSALT) {
			// update legend after a forced layer redraw
			params._OLSALT = layer.params._OLSALT;
		}
		url = Ext.urlAppend(url, Ext.urlEncode(params));
		if (url.toLowerCase().indexOf("request=getlegendgraphic") != -1) {
			if (url.toLowerCase().indexOf("format=") == -1) {
				url = Ext.urlAppend(url, "FORMAT=image/gif");
			}
			// add scale parameter - also if we have the url from the record's
			// styles data field and it is actually a GetLegendGraphic request.
			if (this.useScaleParameter === true) {
				var scale = layer.map.getScale();
				url = Ext.urlAppend(url, "SCALE=" + scale);
			}
		}
		return url;
	},

	/** private: method[update]
	 *  Update the legend, adding, removing or updating
	 *  the per-sublayer box component.
	 */
	update: function() {
		var layer = this.layerRecord.getLayer();
		// In some cases, this update function is called on a layer
		// that has just been removed, see ticket #238.
		// The following check bypass the update if map is not set.
		if(!(layer && layer.map)) {
			return;
		}
		GeoExt.WMSLegend.superclass.update.apply(this, arguments);

		var layerNames, layerName, i, len;

		layerNames = [layer.params.LAYERS].join(",").split(",");

		var destroyList = [];
		var textCmp = this.items.get(0);
		var legendLayers = [];
		this.items.each(function(cmp) {
			if (cmp.itemId) {
				legendLayers.push(cmp.itemId);
			}
			i = layerNames.indexOf(cmp.itemId);
			if(i < 0 && cmp != textCmp) {
				destroyList.push(cmp);
			} else if(cmp !== textCmp){
				layerName = layerNames[i];
				var newUrl = this.getLegendUrl(layerName, layerNames);
				if(!OpenLayers.Util.isEquivalentUrl(newUrl, cmp.url)) {
					cmp.setUrl(newUrl);
				}
			}
		}, this);
		var reverseLayerNames = layerNames.slice(0).reverse();
		if (destroyList.length == 0 && reverseLayerNames.length == legendLayers.length && reverseLayerNames.toString() != legendLayers.toString()) {
			// only reorder of legend items is needed
			// delete all remaining items from the first position mismatch, they will be added in next update in right order
			for(i = 0, len = reverseLayerNames.length; i<len; i++) {
				if (reverseLayerNames[i] != legendLayers[i]) {
					break;
				}
			}
			for(len = reverseLayerNames.length; i<len; i++) {
				var cmp = this.items.get(this.items.getCount()-1);
				// cmp.destroy() does not remove the cmp from
				// its parent container!
				this.remove(cmp);
				cmp.destroy();
			}
		} else {
			for(i = 0, len = destroyList.length; i<len; i++) {
				var cmp = destroyList[i];
				// cmp.destroy() does not remove the cmp from
				// its parent container!
				this.remove(cmp);
				cmp.destroy();
			}

			for(i = 0, len = layerNames.length; i<len; i++) {
				// reverse layers order
				layerName = layerNames[layerNames.length-i-1];
				if(!this.items || !this.getComponent(layerName)) {
					// first item is label, so the first legend image item has index 1
					var index = layer.params.LAYERS.length-layer.params.LAYERS.indexOf(layerName);
					this.insert(index, {
						xtype: "gx_legendimage",
						url: this.getLegendUrl(layerName, layerNames),
						itemId: layerName
					});
				}
			}
			this.doLayout();
		}
	},
});
