(function() {
	'use strict';

	angular
	.module('gl.ui')
	.controller('AccordionController', AccordionController);

	function AccordionController($scope) {
		$scope.selectedAccordionItem = null;
		$scope.isAccordionShown = function(item) {
			return $scope.selectedAccordionItem === item;
		}
		$scope.toggleAccordion = function(item) {
			if ($scope.isAccordionShown(item)) {
				$scope.selectedAccordionItem = null;
			} else {
				$scope.selectedAccordionItem = item;
			}
		};
	}
})();
