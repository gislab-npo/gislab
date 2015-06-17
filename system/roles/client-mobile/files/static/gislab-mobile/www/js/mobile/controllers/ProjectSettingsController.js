(function() {
	'use strict';

	angular
		.module('gl.mobile')
		.controller('ProjectSettingsController', ProjectSettingsController);

	function ProjectSettingsController($scope, gislabMobileClient, projectProvider) {
		$scope.userProjects = [];

		$scope.fetchUserProjects = function() {
			gislabMobileClient.userProjects()
				.success(function(data, status, headers, config) {
					if (angular.isArray(data)) {
						data.forEach(function(projectData) {
							projectData.publish_date_text = new Date(projectData.publication_time_unix*1000).toLocaleString();
							projectData.expiration_date_text = projectData.expiration_time_unix? new Date(projectData.expiration_time_unix*1000).toLocaleString() : '-';
						});
						$scope.userProjects = data;
					}
				})
				.error(function(data, status, headers, config) {
					console.log('error: '+status);
				});
		};
		$scope.fetchUserProjects();
	};
})();
