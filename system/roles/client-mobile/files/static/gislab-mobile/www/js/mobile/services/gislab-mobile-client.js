(function() {
	'use strict';

	angular
		.module('gl.mobile')
		.config(['$httpProvider', function($httpProvider) {
			// Intercept POST requests, convert to standard form encoding
			$httpProvider.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8";
			$httpProvider.defaults.transformRequest.unshift(function (data) {
				var key, result = [];
				for (key in data) {
					if (data.hasOwnProperty(key)) {
						result.push(encodeURIComponent(key) + "=" + encodeURIComponent(data[key]));
					}
				}
				return result.join("&");
			});
		}])
		.factory('gislabMobileClient', ['$http', '$q', gislabMobileClient]);

	function gislabMobileClient($http, $q) {
		function GislabMobileClient() {};

		GislabMobileClient.prototype.login = function(server, username, password) {
			if (username && password) {
				this._secure = true;
				//this.serverUrl = 'https://{0}'.format(server);
				this.serverUrl = 'http://{0}'.format(server);
				return $http.post('{0}/mobile/login/'.format(this.serverUrl), {
						username: username,
						password: password
					}, {
						withCredentials: true
					}
				);
			} else {
				this._secure = false;
				this.serverUrl = 'http://{0}'.format(server);
				return $q.when();
			}
			/*
			return $http({
				method: 'POST',
				url: '{0}/mobile/login/'.format(this.getServerUrl(server)),
				headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
				transformRequest: function(obj) {
					var str = [];
					for(var p in obj)
					str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
					return str.join("&");
				},
				data: {username: username, password: password},
			});*/
		};

		GislabMobileClient.prototype.logout = function() {
			if (this.serverUrl) {
				return $http.get('{0}/mobile/logout/'.format(this.serverUrl), {
						withCredentials: true
					}
				);
			} else {
				return $q.when();
			}
		}

		GislabMobileClient.prototype.project = function(project) {
			var url;
			if (project && project !== 'empty') {
				url = '{0}/mobile/config.json?PROJECT={1}'.format(this.serverUrl, encodeURIComponent(project));
			} else {
				url = '{0}/mobile/config.json?'.format(this.serverUrl);
			}
			return $http.get(url, {
					withCredentials: true
			});
		};

		GislabMobileClient.prototype.userProjects = function() {
			return $http.get('{0}/projects.json'.format(this.serverUrl), {
					withCredentials: true
			});
		};

		return new GislabMobileClient();
	};
})();
