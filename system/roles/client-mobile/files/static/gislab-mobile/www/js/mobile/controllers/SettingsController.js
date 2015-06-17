(function() {
	'use strict';

	angular
		.module('gl.mobile')
		.controller('SettingsController', SettingsController);

	function SettingsController($scope, projectProvider) {
		$scope.showHeaderChanged = function() {
			$scope.updateScreenSize();
		}
		$scope.showScaleLineChanged = function(value) {
			var control = projectProvider.map.getControlByClass(ol.control.ScaleLine);
			control.setMap(value? projectProvider.map : null);
		};
		$scope.showZoomControlsChanged = function(value) {
			var control = projectProvider.map.getControlByClass(ol.control.Zoom);
			control.setMap(value? projectProvider.map : null);
		};
	};
})();
