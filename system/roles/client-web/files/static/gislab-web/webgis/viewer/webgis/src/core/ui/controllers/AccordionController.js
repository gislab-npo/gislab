(function() {
	'use strict';

	angular
	.module('gl.ui')
	.controller('AccordionController', AccordionController);

	function AccordionController($scope) {
		$scope.collapseAccordion = function(accordion) {
			var contentElem = accordion.content;
			var height = contentElem[0].scrollHeight;
			accordion.expanded = false;
			Velocity(
				contentElem[0], {
					maxHeight: 0,
					opacity: 0,
				}, {
					duration: 400,
					easing: "easeInBack",
					begin: function() {
						contentElem.css('maxHeight', height+'px');
					},
				}
			);

		}
		$scope.expandAccordion = function(accordion) {
			var contentElem = accordion.content;
			var height = contentElem[0].scrollHeight;
			accordion.expanded = true;
			Velocity(
				contentElem[0], {
					maxHeight: height,
					opacity: 1,
				}, {
					duration: 400,
					easing: "easeInBack",
					complete: function() {
						contentElem.css('maxHeight', 'none');
					}
				}
			);
		}
		$scope.toggleAccordion = function(accordion) {
			if (!accordion.independent) {
				if ($scope.selectedAccordion && $scope.selectedAccordion !== accordion && $scope.selectedAccordion.expanded) {
					$scope.collapseAccordion($scope.selectedAccordion);
				}
				$scope.selectedAccordion = accordion;	
			}
			if (accordion.expanded) {
				$scope.collapseAccordion(accordion);
			} else {
				$scope.expandAccordion(accordion);
			}
		};
	}
})();
