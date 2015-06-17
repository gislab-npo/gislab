(function() {
	'use strict';

	angular
		.module('gl.map')
		.factory('projectProvider', ['mapBuilder', projectProvider]);

	function projectProvider(mapBuilder) {
		function ProjectProvider() {
			this.map = null;
			this.baseLayers = {
				tree: {},
				list: []
			};
			this.layers = {
				tree: {},
				list: []
			}
		}
		ProjectProvider.prototype.load = function(config) {
			this.config = config;
			if (this.map) {
				this.map.dispose();
			}
			this.baseLayers.tree = config.base_layers;
			this.baseLayers.list = mapBuilder.layersTreeToList({layers: this.baseLayers.tree}, true);
			this.layers.tree = config.layers;
			this.layers.list = mapBuilder.layersTreeToList({layers: this.layers.tree}, true);

			// when no base layers is visible, set first to be visible
			var visibleBaseLayer = this.baseLayers.list.some(function(layerModel) {
				if (layerModel.visible) {
					return true;
				}
			});
			if (!visibleBaseLayer) {
				this.baseLayers.list[0].visible = true;
			}

			this.map = mapBuilder.createMap(config);
		};
		return new ProjectProvider();
	};
})();
