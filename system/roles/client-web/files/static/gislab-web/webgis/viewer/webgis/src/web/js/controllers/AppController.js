(function() {
	'use strict';

	angular
		.module('gl.web')
		.controller('AppController', AppController)
		.controller('LayoutAnimationController', LayoutAnimationController)
		.config(function($mdIconProvider, resourcesRoot) {
			$mdIconProvider
				.defaultIconSet(resourcesRoot+'styles/icons.svg', 32);
		});

	function LayoutAnimationController($scope, $timeout) {
		$scope.$on('ui.layout.toggle', function(e, container) {
			var layoutElem = container.element.parent();
			layoutElem.addClass('ui-layout-animation');
			$timeout(function() {
				layoutElem.removeClass('ui-layout-animation');
			}, 600);
		});
	}
	function AppController($scope, $timeout, $q, projectProvider, layersControl, projectPath, gislabClient, $mdBottomSheet) {
		var bottomSheetPromise = $q.when('');
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
				rowsPerPage: 5,
				limit: 50,
				template: 'templates/toolbar/search.html',
				showTable: function () {
					var tool = this;
					bottomSheetPromise.finally(function() {
						bottomSheetPromise = $mdBottomSheet.show({
							templateUrl: 'templates/search_table.html',
							disableParentScroll: false,
							hasBackdrop: false,
							parent: '.bottom-bar',
							controller: 'SearchController',
							locals: {tool: tool}
						});
						bottomSheetPromise.catch(function() {
							bottomSheetPromise = $q.when('');
							tool.activated = false;
						});
					});
				},
				activate: function () {
					if (this.layerIndex) {
						this.showTable();
					}
				},
				deactivate: function () {
					$mdBottomSheet.hide();
				}
			}, {
				title: 'Identify features by mouse click',
				icon: 'circle-i',
				toggleGroup: '1',
				rowsPerPage: 5,
				limit: 10,
				template: 'templates/toolbar/identification.html',
				activate: function () {
					var tool = this;
					bottomSheetPromise.finally(function() {
						bottomSheetPromise = $mdBottomSheet.show({
							templateUrl: 'templates/identification_table.html',
							clickOutsideToClose: false,
							disableParentScroll: false,
							parent: '.bottom-bar',
							controller: 'IdentificationController',
							locals: {tool: tool}
						});
						bottomSheetPromise.catch(function() {
							bottomSheetPromise = $q.when('');
							tool.activated = false;
						});
					});
				},
				deactivate: function() {
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
					$scope.toolClicked($scope.tools[4]);
				}
			})
	};
})();
