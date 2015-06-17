(function() {
	'use strict';

	angular
		.module('gl.utils')
		.directive('glClick', glClick)
		.directive('glOpenInBrowser', glOpenInBrowser);

	function glClick($parse) {
		return {
			compile: function(elem, attr) {
				var clickHandler = $parse(attr.glClick);
				return function(scope, elem) {
					post: {
						elem.on('click', function(event) {
							scope.$apply(function() {
								clickHandler(scope, {$event: event});
							});
						});
					}
				};
			}
		};
	};

	function glOpenInBrowser() {
		return {
			restrict: 'A',
			link: function (scope, iElem, iAttrs) {
				iElem.on('click', function(event) {
					window.open(iAttrs.href, '_system', 'location=yes');
					event.preventDefault();
				});
			}
		};
	};
})();
