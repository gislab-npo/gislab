(function() {
	'use strict';

	angular
		.module('gl.mobile')
		.controller('MobileAppController', MobileAppController);

	function MobileAppController($scope, $timeout, $q, $localStorage, gislabMobileClient, projectProvider, layersControl, locationService, TabbarView, TabbarSlideAnimator) {
		TabbarView.registerAnimator('slide', new TabbarSlideAnimator());
		$scope.$storage = $localStorage;
		$scope.currentProject = null;
		$scope.currentServer = null;

		$scope.ui = {
			tools_layers_tab: 0,
			tools_settings_tab: 0,
		};
		$scope.ui.toolbar = [
			{
				icon: 'ion-social-buffer',
				page: 'pages/tools/layers.html',
				persistent: true,
				disabled: true,
				activate: function() {
					if ($scope.app.panel.layersTreeView) {
						$scope.app.panel.layersTreeView.setSelectedNodes(layersControl.getVisibleLayers(projectProvider.map));
					}
				},
			}, {
				icon: 'ion-android-color-palette',
				page: 'pages/tools/legend.html',
				persistent: true,
				disabled: true
			}, {
				icon: 'ion-qr-scanner',
				toggle: false,
				disabled: true,
				callback: function() {
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
					projectProvider.map.getView().fitExtent(projectProvider.config.project_extent, projectProvider.map.getSize());
				}
			}, {
				icon: 'ion-location',
				disabled: true,
				//toggle: true,
				toggle: false,
				callback: function() {
					if (this.icon === 'ion-android-locate') {
						this.activated = false;
						this.icon = 'ion-location';
						locationService.deactivate(projectProvider.map);
					} else {
						if (!this.activated) {
							this.activated = true;
							locationService.setAutoPan(false);
							locationService.activate(projectProvider.map);
						} else {
							this.icon = 'ion-android-locate';
							locationService.setAutoPan(true);
						}
					}
				}
			}, /*{
				icon: 'ion-search'
			}, {
				icon: 'ion-information-circled'
			}, {
				faIcon:'fa-expand'
			}, {
				icon: 'ion-edit',
				page: 'pages/tools/drawings.html',
				persistent: true,
			}, */{
				icon: 'ion-gear-b',
				page: 'pages/settings/settings.html',
				disabled: false
			}
		];

		$scope.toolTaped = function(tool) {
			//console.log(tool);
			if (tool.page) {
				if (!tool.activated) {
					var switchTool = false;
					$scope.ui.toolbar.forEach(function(item) {
						if (item.page && item.activated) {
							item.activated = false;
							switchTool = true;
						}
					});
					var animation = $scope.app.menu.isMenuOpened()? 'slide' : 'none';
					if (tool.activate) {
						tool.activate();
					}
					$scope.app.panel.tabbar.setActiveTab(tool._tab_index, {animation: animation});
					if (!switchTool) {
						$timeout(function() {
							$scope.app.menu.openMenu({autoCloseDisabled: true});
						});
					}
				} else {
					$scope.app.menu.closeMenu();
				}
				//$scope.app.menu.toggleMenu();
				tool.activated = !tool.activated;
			} else if (!tool.toggle) {
				if (tool.callback) {
					tool.callback();
				}
			} else {
				tool.activated = !tool.activated;
			}
		};

		$scope.login = function() {
			var login = $q.defer();
			gislabMobileClient.login($scope.$storage.serverUrl, $scope.$storage.username, $scope.$storage.password)
				.then(function() {
					$scope.currentServer = '{0}:{1}:{2}'.format($scope.$storage.serverUrl, $scope.$storage.username, $scope.$storage.password);
					login.resolve();
				}, function() {
					$scope.currentServer = null;
					login.reject();
				});
			return login.promise;
		}
		$scope.loginAndLoadProject = function(viewConfig) {
			if ($scope.$storage.serverUrl) {
				$scope.showProgressDialog($scope.app.progressBar, 'Login to GIS.lab server');
				$scope.login()
					.catch(function() {
						$scope.loginFailed = true;
					})
					.finally(function () {
						$scope.setProgressBarMessage('Loading project ...');
						$scope.loadProject($scope.$storage.project, viewConfig)
							.catch(function() {
								$scope.invalidProject = true;
							})
							.finally(function() {
								$scope.hideProgressDialog($scope.app.progressBar, 800, function() {
									if ($scope.loginFailed && $scope.invalidProject) {
										ons.notification.alert({
											title: 'Warning',
											message: 'Login to GIS.lab server has failed and failed to load project as Guest user.'
										});
									} else if ($scope.loginFailed) {
										ons.notification.alert({
											title: 'Warning',
											message: 'Login to GIS.lab server has failed. Continue as Guest user.'
										});
										$scope.loginFailed = null;
									} else if ($scope.invalidProject) {
										ons.notification.alert({
											title: 'Warning',
											message: 'Failed to load project.'
										});
									}
									$scope.loginFailed = null;
									$scope.invalidProject = null;
								});
							});
					});
			} else {
				$scope.loadProject(null);
				$scope.app.wizard.carousel.setActiveCarouselItemIndex(0);
				$scope.app.wizard.dialog.show();
			}
		}

		ons.ready(function() {
			console.log('ons ready');
			setImmediate(function() {
				$scope.app.menu.on('postclose', function() {
					$scope.ui.toolbar.forEach(function(tool) {
						if (tool.page && tool.activated) {
							$timeout(function() {
								tool.activated = false;
							});
						}
					});
				});
			});
			$scope.app.navigator.on('postpop', function(evt) {
				if (evt.leavePage.page === 'pages/settings/project.html' && $scope.currentProject !== $scope.$storage.project) {
					$scope.loadProjectWithProgressBar($scope.$storage.project);
				}
				if (evt.leavePage.page === 'pages/settings/server.html') {
					var server = '{0}:{1}:{2}'.format($scope.$storage.serverUrl, $scope.$storage.username, $scope.$storage.password);
					if ($scope.currentServer !== server) {
						if ($scope.currentServer) {
							gislabMobileClient.logout()
								.finally(function() {
									$scope.loginAndLoadProject();
								});
						} else {
							$scope.loginAndLoadProject();
						}
					}
				}
				if (evt.enterPage.page === 'map_container.html' && projectProvider.map && projectProvider.map.getSize()[0] === 0) {
					projectProvider.map.updateSize();
				}
			});

			$scope.updateScreenSize();
			if ($scope.$storage.mapState && $scope.$storage.mapState.project === $scope.$storage.project) {
				$scope.loginAndLoadProject($scope.$storage.mapState);
			} else {
				$scope.loginAndLoadProject();
			}
			//$scope.app.wizard.dialog.show();
		});

		$scope.updateScreenSize = function() {
			var width, height;
			if (window.orientation === 0 || window.orientation === 180) {
				width = Math.min(window.innerWidth, window.innerHeight);
				height = Math.max(window.innerWidth, window.innerHeight);
			} else {
				width = Math.max(window.innerWidth, window.innerHeight);
				height = Math.min(window.innerWidth, window.innerHeight);
			}
			$scope.screenWidth = width;
			$scope.screenHeight = height;
			if (projectProvider.map) {
				projectProvider.map.updateSize();
			}
			//console.log('orientation: {0}'.format(window.orientation));
			//console.log('screenWidth: {0}'.format($scope.screenWidth));
			//console.log('screenHeight: {0}'.format($scope.screenHeight));
		};

		$scope.showProgressDialog = function(dialog, msg) {
			if (angular.isDefined(msg)) {
				$scope.setProgressBarMessage(msg);
			}
			dialog._showTime = Date.now();
			dialog.show();
		};
		$scope.hideProgressDialog = function(dialog, minShowTime, done) {
			var args = Array.prototype.slice.call(arguments, 4);
			var thiz = arguments[3] || null;
			var elapsed = Date.now() - dialog._showTime;
			dialog._showTime = 0;
			if (elapsed >= minShowTime) {
				dialog.hide();
				if (angular.isFunction(done)) {
					done.apply(thiz, args);
				}
			} else {
				$timeout(function() {
					dialog.hide();
					if (angular.isFunction(done)) {
						done.apply(thiz, args);
					}
				}, minShowTime-elapsed);
			}
		};
		$scope.setProgressBarMessage = function(msg) {
			$scope.progressBarMessage = msg;
		};

		$scope.loadProject = function(projectName, viewConfig) {
			var task = $q.defer();
			//$scope.showProgressDialog($scope.app.modal.loadingProject)
			console.log('loadProject '+projectName);
			$scope.$storage.project = projectName;

			if ($scope.$storage.serverUrl) {
				gislabMobileClient.project(projectName)
					.success(function(data, status, headers, config) {
						projectProvider.load(data);
						$scope.currentProject = projectName;
						if (projectProvider.map) {
							$scope.ui.toolbar[0].disabled = false;
							$scope.ui.toolbar[1].disabled = !angular.isDefined(projectProvider.map.getLayer('qgislayer'));
							$scope.ui.toolbar[2].disabled = false;
							$scope.ui.toolbar[3].disabled = false;
							var scaleLineControl = new ol.control.ScaleLine();
							projectProvider.map.addControl(scaleLineControl);
							// set visibility of map controls by user settings
							if (!$scope.$storage.showScaleLine) {
								scaleLineControl.setMap(null);
							}
							if (!$scope.$storage.showZoomControls) {
								var zoomControl = projectProvider.map.getControlByClass(ol.control.Zoom);
								zoomControl.setMap(null);
							}
							//$scope.$storage.recentProjects = [];
							var currentProjectData = {
								project: data.project,
								author: data.author,
								publish_date_text: data.publish_date,
								expiration_date: data.expiration_date
							};
							if (!$scope.$storage.recentProjects) {
								$scope.$storage.recentProjects = [currentProjectData];
							} else {
								var index = -1;
								$scope.$storage.recentProjects.some(function(projectData, i) {
									if (projectData.project === currentProjectData.project) {
										index = i;
										return true;
									}
								});
								if (index !== -1) {
									$scope.$storage.recentProjects.splice(index, 1);
								}
								$scope.$storage.recentProjects.splice(0, 0, currentProjectData);
							}
							$scope.project = data;
							// initialize map page
							$timeout(function() {
								//$scope.app.navigator.resetToPage('map_container.html');
								$scope.app.menu.closeMenu();
								$scope.app.menu.setMenuPage('panel_tab_container.html');
								$scope.app.menu.setMainPage('map.html');
								$timeout(function() {
									projectProvider.map.setTarget('map');
									if (viewConfig) {
										projectProvider.map.getView().setCenter(viewConfig.center);
										projectProvider.map.getView().setZoom(viewConfig.zoom);
										projectProvider.map.getView().setRotation(viewConfig.rotation);
										if (viewConfig.baseLayer) {
											layersControl.setBaseLayer(projectProvider.map, viewConfig.baseLayer);
											projectProvider.baseLayers.list.forEach(function(baseLayerModel) {
												baseLayerModel.visible = viewConfig.baseLayer === baseLayerModel.name;
											});
										}
										if (viewConfig.visibleLayers) {
											layersControl.setVisibleLayers(projectProvider.map, viewConfig.visibleLayers);
											projectProvider.layers.list.forEach(function(layerModel) {
												layerModel.visible = viewConfig.visibleLayers.indexOf(layerModel.name) !== -1;
											});
										}
									} else {
										projectProvider.map.getView().fitExtent(data.zoom_extent, projectProvider.map.getSize());
									}
									task.resolve();
								});
							});
						} else {
							task.reject();
						}
					})
					.error(function(data, status, headers, config) {
						task.reject();
					})
			} else {
				console.log('No MAP');
				if (projectProvider.map) {
					projectProvider.map.dispose();
					projectProvider.map = null;
					$scope.ui.toolbar[0].disabled = true;
					$scope.ui.toolbar[1].disabled = true;
					$scope.ui.toolbar[2].disabled = true;
					$scope.ui.toolbar[3].disabled = true;
					$scope.app.menu.closeMenu();
					$scope.app.menu.setMenuPage('panel_tab_container.html');
					$scope.app.menu.setMainPage('map.html');
				}
				task.resolve();
			}
			return task.promise;
		};
		$scope.loadProjectWithProgressBar = function(projectName) {
			$scope.showProgressDialog($scope.app.progressBar, 'Loading project ...');
			$scope.loadProject(projectName)
				.catch(function() {
					$scope.invalidProject = true;
				})
				.finally(function() {
					$scope.hideProgressDialog($scope.app.progressBar, 500, function() {
						if ($scope.invalidProject) {
							ons.notification.alert({
								title: 'Warning',
								message: 'Failed to load project.'
							});
							$scope.invalidProject = null;
						}
					});
				});
		};
		$scope.saveMapState = function() {
			var map = projectProvider.map;
			if (map) {
				var baseLayer = layersControl.getVisibleBaseLayer(map);
				$scope.$apply(function() {
					$scope.$storage.mapState = {
						project: $scope.$storage.project,
						center: map.getView().getCenter(),
						zoom: map.getView().getZoom(),
						rotation: map.getView().getRotation(),
						visibleLayers: layersControl.getVisibleLayers(map),
						baseLayer: baseLayer? baseLayer.get('name') : ''
					};
				});
			}
		};

		// device APIs are available
		function onDeviceReady() {
			setTimeout(function() {
				navigator.splashscreen.hide();
			}, 200);
			ons.setDefaultDeviceBackButtonListener(function() {
				if (!$scope.exitDialogShown) {
					$scope.exitDialogShown = true;
					ons.notification.confirm({
						message: 'Are you sure to close the app?',
						callback: function(index) {
							if (index === 1) { // OK button
								$scope.saveMapState();
								navigator.app.exitApp(); // Close the app
							}
							$scope.exitDialogShown = false;
						}
					});
				}
			});

			window.addEventListener('orientationchange', function() {
				$scope.updateScreenSize();
			});
			document.addEventListener("pause", onPause, false);
			document.addEventListener("resume", function() {
				/*
				console.log("--------RESUMED--------");
				*/
			}, false);

		};
		function onPause() {
			console.log("--------PAUSE--------");
			$scope.saveMapState();
		}
		console.log('register deviceready');
		document.addEventListener("deviceready", onDeviceReady, false);
	};
})();
