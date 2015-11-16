(function() {
	'use strict';
	angular
		.module('templates', []); // module for compiled templates
	angular
		.module('gl.web', [
			'templates',
			'ngMaterial',
			'ui.layout',
			'md.data.table',
			'gl.ui',
			'gl.utils',
			'gl.map',
			'gl.legend',
			'gl.layersControl',
			'gl.features'
		]);
})();
