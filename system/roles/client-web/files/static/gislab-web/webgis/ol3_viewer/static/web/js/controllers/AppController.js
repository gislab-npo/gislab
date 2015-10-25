(function() {
	'use strict';

	angular
		.module('gl.web')
		.controller('AppController', AppController)
		.config(function($mdIconProvider, resourcesRoot) {
			$mdIconProvider
				.defaultIconSet(resourcesRoot+'styles/gislab/icons.svg', 32);
		});

	function AppController($scope, $timeout, $q, $mdSidenav, projectProvider, layersControl, projectPath, gislabClient) {
		$scope.openLeftMenu = function() {
			$mdSidenav('left').toggle();
		};
		gislabClient.project(projectPath)
			.then(function(data) {
				$scope.title = data.root_title;
				projectProvider.load(data);
				if (projectProvider.map) {
					projectProvider.map.setTarget('map');
					projectProvider.map.getView().fit(data.zoom_extent, projectProvider.map.getSize());
					//layersControl.setVisibleLayers(projectProvider.map, ['Places', 'Roads', 'Visegrad Four']);
					$scope.project = projectProvider.config;
				}
			})
		/*
		var baseLayers = [
			{
				title: "Blank",
				name: "blank",
				visible: false
			}, {
				title: "Open Street Map",
				name: "OSM",
				visible: false
			}, {
				title: "Ortofoto",
				name: "ortofoto",
				layers: [
					{
						title: "Whole world",
						name: "world"
					}, {
						title: "Half world",
						name: "half"
					}
				]
			}
		];
		var layers = [
			{
				title: "Capitals",
				name: "Layer1",
				geom_type: "point",
				visible: true,
				queryable: true,
				metadata: {
					abstract: "The capitals of central Europe",
				}
			}, {
				title: "Group",
				name: "group",
				layers: [
					{
						title: "Layer 2",
						name: "Layer2",
						geom_type: "line",
						visible: false
					}, {
						title: "Layer 3",
						name: "Layer3",
						geom_type: "polygon",
						visible: true,
						queryable: true
					}, {
						title: "Other",
						name: "nested_group",
						layers: [
							{
								title: "Other Countries",
								name: "layer4",
								geom_type: "polygon",
								visible: true,
								metadata: {
									abstract: "Other Central European countries"
								}
							}
						]
					}

				]
			}
		];
		var project = {topics: [
			{
				title: 'Topic',
				abstract: ''
			}
		]};
		projectProvider.config = project;
		projectProvider.layers = {tree: layers, list: []};
		projectProvider.baseLayers = {tree: baseLayers, list: []};
		$scope.project = project;
		*/
	};
})();
