(function() {
	'use strict';

	angular
		.module('gl.legend')
		.controller('LegendController', LegendController);

	function LegendController($scope, $timeout, projectProvider) {
		$scope.layers = projectProvider.layers;
		
		$scope.updateLegendUrls = function() {
			var layerSource = projectProvider.map.getLayer('qgislayer').getSource();
			var view = projectProvider.map.getView();
			$scope.layers.list.forEach(function(layer_data) {
				layer_data.legendUrl = layerSource.getLegendUrl(layer_data.name, view);
			});
		};

		if (projectProvider.map) {
			$scope.updateLegendUrls();
		}
		/*
		projectProvider.map.getView().on('change:resolution', function() {
			console.log('Zoom changed...');
			$timeout(function() {
				//$scope.updateLegendUrls();
			});
		});
*/
	};
})();
