(function() {
	'use strict';

	angular
	.module('gl.ui')
	.animation('.height-animation', function() {
		return {
			beforeAddClass : function(element, className, done, options) {
				var height = element[0].scrollHeight;
				element.css('maxHeight', height+'px');
				element.css('opacity', '1');
				done();
			},
			beforeRemoveClass : function(element, className, done) {
				var height = element[0].scrollHeight;
				element.css('maxHeight', '0px');
				element.css('opacity', '0');
				done();
			}
		};
	})
	.controller('AccordionController2', AccordionController2);

	function AccordionController2($scope, $animate) {
		$scope.collapseAccordion = function(accordion) {
			var contentElem = accordion.content;
			var height = contentElem[0].scrollHeight;
			accordion.expanded = false;
			contentElem.css('maxHeight', height+'px');
			$animate.removeClass(contentElem, 'height-animation');
		}
		$scope.expandAccordion = function(accordion) {
			var contentElem = accordion.content;
			accordion.expanded = true;
			$animate.addClass(contentElem, 'height-animation')
				.then(function() {
					contentElem.css('maxHeight', 'none');
				});
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
