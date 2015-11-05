(function() {
	'use strict';

	angular
		.module('gl.features')
		.controller('FeaturesController', FeaturesController);

	function FeaturesController($scope, projectProvider, gislabClient) {
		var featuresLayers = {};
		var selectionControls = {};
		var selectControl;
		var layersAttributes = {};

		/* Collect info about layer attributes (aliases) */
		projectProvider.layers.list.forEach(function(layer) {
			var attributesData = {};
			layer.attributes.forEach(function(attr) {
				attributesData[attr.name] = {
					alias: attr.alias,
					type: attr.type
				}
			})
			layersAttributes[layer.name] = attributesData;
		});

		var createVectorLayer = function(layername) {
			var vectorLayer = new ol.layer.Vector({
				source: new ol.source.Vector({
					//projection: ol.proj.get('EPSG:4326')
				}),
				style: new ol.style.Style({
					stroke: new ol.style.Stroke({
						color: [250, 250, 25, 0.8],
						width: 2
					}),
					fill: new ol.style.Fill({
						color: [250, 250, 25, 0.5]
					}),
					image: new ol.style.Circle({
						stroke: new ol.style.Stroke({
							color: [250, 250, 25, 0.8],
							width: 2
						}),
						fill: new ol.style.Fill({
							color: [250, 250, 25, 0.5]
						}),
						radius: 5
					}),
				}),
				visible: false
			});
			vectorLayer.set('name', layername);
			featuresLayers[layername] = vectorLayer;
			projectProvider.map.addLayer(vectorLayer);
			return vectorLayer;
		}

		var createLayerSelectControl = function(layername) {
			var selectControl = new ol.interaction.Select({
				condition: ol.events.condition.never,
				layers: [featuresLayers[layername]],
				style: new ol.style.Style({
					stroke: new ol.style.Stroke({
						color: [102, 204, 204, 0.8],
						width: 3
					}),
					fill: new ol.style.Stroke({
						color: [102, 204, 204, 0.5],
					}),
					image: new ol.style.Circle({
						stroke: new ol.style.Stroke({
							color: [102, 204, 204, 0.8],
							width: 2
						}),
						fill: new ol.style.Fill({
							color: [102, 204, 204, 0.5],
						}),
						radius: 5
					}),
				})
			});
			selectionControls[layername] = selectControl;
			projectProvider.map.addInteraction(selectControl);
			return selectControl;
		}

		$scope.selectedFeature = null;
		$scope.selectFeature = function(feature) {
			$scope.selectedFeature = feature;
			selectControl.getFeatures().clear();
			selectControl.getFeatures().push(feature);
		}

		$scope.getFeatureProperties = function(feature) {
			var fid = feature.getId();
			var layername = fid.substring(0, fid.lastIndexOf('.'));
			var layerAttrs = layersAttributes[layername];
			var properties = [];
			feature.getKeys().forEach(function(property) {
				if (property !== feature.getGeometryName() && property !== 'boundedBy') {
					properties.push({
						key: property,
						label: layerAttrs[property].alias || property
					});
				}
			});
			return properties;
		};

		$scope.setFeaturesLayer = function(layername) {
			for (var lname in featuresLayers) {
				featuresLayers[lname].setVisible(lname === layername);
			}

			selectControl = selectionControls[layername] || createLayerSelectControl(layername);
			for (var lname in selectionControls) {
				selectionControls[lname].setActive(lname === layername);
				selectionControls[lname].setMap(lname === layername? projectProvider.map: null);
			}
		};

		$scope.setFeatures = function(features) {
			// clear prevoius selection
			if (selectControl) {
				selectControl.getFeatures().clear();
			}
			for (var layername in featuresLayers) {
				featuresLayers[layername].getSource().clear();
			}

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
				var featuresCategories = [];
				for (var layername in layerFeatures) {
					var vectorLayer = featuresLayers[layername] || createVectorLayer(layername);
					vectorLayer.getSource().addFeatures(layerFeatures[layername]);
					featuresCategories.push({
						layer: layername,
						features: layerFeatures[layername]
					});
				}
				$scope.featuresCategories = featuresCategories;
			} else {
				$scope.featuresCategories = null;
			}
		}
		if ($scope.features) {
			$scope.setFeatures($scope.features);
		}

		$scope.$on("$destroy", function() {
			for (var layername in featuresLayers) {
				featuresLayers[layername].getSource().clear();
			}
			for (var layername in selectionControls) {
				selectionControls[layername].getFeatures().clear();
				selectionControls[layername].setMap(null);
			}
		});
	};
})();
