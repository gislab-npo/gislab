(function() {
	'use strict';

	angular
		.module('gl.features')
		.controller('IdentificationController', IdentificationController);

	function IdentificationController($scope, $timeout, projectProvider, gislabClient, featuresViewer, tool) {
		console.log('IdentificationController: INIT');
		$scope.tool = tool;
		$scope.showTabsHeader = false;
		featuresViewer.initialize();

		$scope.$watch('selectedTab', function (value) {
			if (angular.isDefined(value) && $scope.layers) {
				featuresViewer.setActiveFeaturesLayer($scope.layers[value].name);
			}
		});

		$scope.selectFeature = function (feature) {
			featuresViewer.selectFeature(feature);
			$scope.selectedFeature = feature;
		};

		function setFeatures (features) {
			// clear prevoius selection

			if (features.length > 0) {
				// organize features by layer name
				var layerFeatures = {};
				features.forEach(function(feature) {
					if (feature instanceof ol.Feature) {
						var fid = feature.getId();
						var layername = fid.substring(0, fid.lastIndexOf('.'));
						if (!layerFeatures.hasOwnProperty(layername)) {
							layerFeatures[layername] = [];
						}
						layerFeatures[layername].push(feature);
					}
				});
				var layers = [];
				for (var layername in layerFeatures) {
					layers.push({
						name: layername,
						attributes: featuresViewer.getLayerAttributes(layername),
						features: layerFeatures[layername]
					});
				}
				featuresViewer.setLayersFeatures(layerFeatures);
				featuresViewer.setActiveFeaturesLayer(layers[0].name);
				$scope.showTabsHeader = $scope.tool.identificationLayer? false : true;
				$scope.layers = layers;
			} else {
				featuresViewer.setActiveFeaturesLayer('');
				$scope.showTabsHeader = true;
				$scope.layers = [{
					name: 'No features',
					attributes: [],
					features: []
				}];
			}
		}

		var mapClickListener = projectProvider.map.on('singleclick', function (evt) {
			var source = projectProvider.map.getLayer('qgislayer').getSource();
			var layers = $scope.tool.identificationLayer? [$scope.tool.identificationLayer] : source.getVisibleLayers();
			var featureInfoUrl = source.getGetFeatureInfoUrl(projectProvider.map, evt.pixel, layers);
			var featureType = [];
			layers.forEach(function(layer) {
				featureType.push('qgs:'+layer.replace(' ', ''));
			});
			$scope.progress = gislabClient.get(featureInfoUrl).then(function(data) {
				var gml = new ol.format.GML2({
					featureNS: {'qgs': 'http://qgis.org/gml'},
					featureType: featureType
				});
				var features = gml.readFeatures(data);
				setFeatures(features);
			});
		});

		$scope.$on("$destroy", function() {
			console.log('IdentificationController: DESTROY');
			projectProvider.map.unByKey(mapClickListener);
			featuresViewer.setActiveFeaturesLayer('');
			featuresViewer.selectFeature(null);
		});
	};
})();
