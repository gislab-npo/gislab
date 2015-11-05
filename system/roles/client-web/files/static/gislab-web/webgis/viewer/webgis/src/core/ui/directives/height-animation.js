(function() {
	'use strict';

	angular
	.module('gl.ui')
	.animation('.height-anim', function() {
		return {
			beforeAddClass : function(element, className, done, options) {
				var height = element[0].scrollHeight;
				if (options.skip) {
					element.css('height', 'auto');
				} else {
					element.css('height', '{0}px'.format(height));
				}
				done();
			},
			beforeRemoveClass : function(element, className, done) {
				var height = element[0].scrollHeight;
				element.css('height', '{0}px'.format(height));
				done();
			}
		};
	})
	.directive('glHeightAnimation', glHeightAnimation)
	.directive('glFixedHeight', glFixedHeight);

	function glHeightAnimation() {
		return {
			restrict: 'A',
			controller: ['$scope', '$animate', function($scope, $animate) {
				$scope.setup = function(visibilityModel, iElem) {
					var skip = true;
					$scope.$watch(visibilityModel, function(visible) {
						if (visible) {
							$animate.removeClass(iElem, 'height-anim').then(function() {
								iElem.css('height', 'auto');
							});
						} else {
							$animate.addClass(iElem, 'height-anim', {skip: skip});
						}
						skip = false;
					});
				};
			}],
			link: function(scope, iElem, iAttrs, ctrl) {
				var visibilityModel = iAttrs.glHeightAnimation || iAttrs.ngShow || iAttrs.ngHide || iAttrs.ngIf;
				scope.setup(visibilityModel, iElem);
			}
		};
	};

	function glFixedHeight($timeout) {
		return {
			restrict: 'A',
			compile: function(tElem, tAttrs) {
				tElem[0].setAttribute('style', 'display: block!important;visibility: hidden!important;');
				return {
					post: function(scope, iElem, iAttrs) {
						$timeout(function() {
							var height = iElem[0].scrollHeight;
							//iElem.parent()[0].setAttribute('style', 'max-height: {0}px'.format(height));
							iElem[0].setAttribute('style', 'height: {0}px'.format(height));
						});
					}
				}
			}
		};
	};
})();
