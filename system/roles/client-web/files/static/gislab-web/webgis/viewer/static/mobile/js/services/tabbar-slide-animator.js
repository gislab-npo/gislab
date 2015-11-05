(function() {
	'use strict';

	angular
		.module('gl.mobile')
		.factory('TabbarSlideAnimator', ['TabbarAnimator', 'TabbarView', TabbarSlideAnimator]);

	function TabbarSlideAnimator(TabbarAnimator, TabbarView) {
		var TabbarSlideAnimator = TabbarAnimator.extend({
			/**
			 * @param {jqLite} enterPage
			 * @param {jqLite} leavePage
			 */
			apply: function(enterPage, leavePage, done) {
				animit.runAll(
					animit(enterPage[0])
						.queue({
							transform: 'translate3D(100%, 0, 0)',
							opacity: 1
						})
						.queue({
							transform: 'translate3D(0, 0, 0)',
							opacity: 1
						}, {
							duration: 0.2,
							timing: 'linear'
						})
						.resetStyle()
						.queue(function(callback) {
							done();
							callback();
						}),
					animit(leavePage[0])
						.queue({
							transform: 'translate3D(0, 0, 0)',
							opacity: 1
						})
						.queue({
							transform: 'translate3D(-100%, 0, 0)',
							opacity: 1
						}, {
							duration: 0.2,
							timing: 'linear'
						})
						.resetStyle()
						.queue({
							display: 'none',
						})
				);
			}
		});
		return TabbarSlideAnimator;
	}
})();
