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
		function GislabMobileClient() {
			this.currentRequest = null;
		};

		GislabMobileClient.prototype._deferredRequest = function(httpParams) {
			var deferredAbort = $q.defer();
			var requestParams = angular.extend({
					timeout: deferredAbort.promise
				}, httpParams);
			var request = $http(requestParams);
			var promise = request.then(
				function (response) {
					return response.data;
				}, function (response) {
					return $q.reject({canceled: promise.canceled === true});
				}
			);
			promise.abort = function() {
				promise.canceled = true;
				deferredAbort.resolve();
			}
			promise.finally(function() {
				promise.abort = angular.noop;
				deferredAbort = request = promise = null;
			});
			this.currentRequest = promise;
			return promise;
		};

		GislabMobileClient.prototype.abortRequest = function() {
			if (this.currentRequest && this.currentRequest.abort) {
				this.currentRequest.abort();
			}
		};

		GislabMobileClient.prototype.login = function(server, username, password) {
			if (username && password) {
				this._secure = true;
				//this.serverUrl = 'https://{0}'.format(server);
				this.serverUrl = 'http://{0}'.format(server);
				return this._deferredRequest({
					url: '{0}/mobile/login/'.format(this.serverUrl),
					method: 'post',
					withCredentials: true,
					data: {
						username: username,
						password: password
					}
				});
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
				return this._deferredRequest({
					url: '{0}/mobile/logout/'.format(this.serverUrl),
					withCredentials: true
				});
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
			return this._deferredRequest({
				url: url,
				method: 'get',
				withCredentials: true
			});
		};

		GislabMobileClient.prototype.userProjects = function() {
			return this._deferredRequest({
				url: '{0}/projects.json'.format(this.serverUrl),
				method: 'get',
				withCredentials: true
			});
		};

		return new GislabMobileClient();
	};
})();
