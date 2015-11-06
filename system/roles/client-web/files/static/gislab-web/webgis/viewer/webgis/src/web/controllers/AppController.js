(function() {
	'use strict';

	angular
		.module('gl.web')
		.controller('AppController', AppController)
		.config(function($mdIconProvider, resourcesRoot) {
			$mdIconProvider
				.defaultIconSet(resourcesRoot+'styles/icons.svg', 32);
		});

	function AppController($scope, $timeout, $q, $mdSidenav, projectProvider, layersControl, projectPath, resourcesRoot, gislabClient, $mdBottomSheet) {
		$scope.tools = [
			{
				title: 'Zoom to max extent',
				icon: 'zoom-max',
				action: function() {
					var map = projectProvider.map;
					var pan = ol.animation.pan({
						duration: 300,
						source: map.getView().getCenter()
					});
					var zoom = ol.animation.zoom({
						duration: 300,
						resolution: map.getView().getResolution()
					});
					map.beforeRender(pan, zoom);
					map.getView().fit(projectProvider.config.project_extent, map.getSize());
				}
			}, {
				title: 'Print output creation',
				icon: 'printer',
				toggleGroup: '1',
				disabled: true
			}, {
				title: 'Draw points, lines, polygons',
				icon: 'pen',
				toggleGroup: '2',
				disabled: true
			}, {
				title: 'Search features by attributes',
				icon: 'binocular',
				toggleGroup: '1',
				activate: function() {},
				deactivate: function() {}
			}, {
				title: 'Identify features by mouse click',
				icon: 'circle-i',
				toggleGroup: '1',
				activate: function() {
					var featuresScope;
					this.mapClickListener = projectProvider.map.on('singleclick', function(evt) {
						var source = projectProvider.map.getLayer('qgislayer').getSource();
						var layers = this.identificationLayer? [this.identificationLayer] : source.getVisibleLayers();
						var featureInfoUrl = source.getGetFeatureInfoUrl(projectProvider.map, evt.pixel, layers);
						var featureType = [];
						layers.forEach(function(layer) {
							featureType.push('qgs:'+layer.replace(' ', ''));
						});
						gislabClient.get(featureInfoUrl).then(function(data) {
							var gml = new ol.format.GML2({
								featureNS: {'qgs': 'http://qgis.org/gml'},
								featureType: featureType
							});
							var features = gml.readFeatures(data);
							if (!featuresScope) {
								featuresScope = $scope.$new(true, $scope);
								featuresScope.features = features;
								$mdBottomSheet.show({
									templateUrl: resourcesRoot+'features_panel.html',
									clickOutsideToClose: false,
									disableParentScroll: false,
									controller: 'FeaturesController',
									scope: featuresScope,
									parent: '.bottom-bar'
								}).finally(function() {
									featuresScope.setFeatures([]);
									featuresScope = null;
								});
							} else {
								featuresScope.setFeatures(features);
							}
						});
					}, this);
				},
				deactivate: function() {
					projectProvider.map.unByKey(this.mapClickListener);
					$mdBottomSheet.hide();
				}
			}
		];
		$scope.toolClicked = function(tool) {
			if (angular.isFunction(tool.action)) {
				tool.action();
			}
			if (tool.toggleGroup) {
				if (!tool.activated) {
					$scope.tools.forEach(function(t) {
						if (t.activated && tool !== t && t.toggleGroup === tool.toggleGroup) {
							t.activated = false;
							t.deactivate();
						}
					});
				}
				tool.activated = !tool.activated;
				if (tool.activated) {
					tool.activate();
				} else {
					tool.deactivate();
				}
			}
		};

		$scope.openLeftMenu = function() {
			$mdSidenav('left').toggle();
		};
		gislabClient.project(projectPath)
			.then(function(data) {
				$scope.title = data.root_title;
				projectProvider.load(data);
				console.log(data);
				var mapElem = angular.element(document.getElementById('map'));
				mapElem.css('height', mapElem.parent()[0].scrollHeight+'px');
				if (projectProvider.map) {
					projectProvider.map.setTarget('map');
					projectProvider.map.getView().fit(data.zoom_extent, projectProvider.map.getSize());
					projectProvider.map.addControl(new ol.control.ScaleLine());
					$scope.project = projectProvider;
					//mapElem.css('height', '100%');
				}
			})
	};
})();
