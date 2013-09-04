var TOP_TEN_URL = _.template('/api/top/f/<%= topTenFilter %>/');

var app = angular.module('app', []);

app.factory('$routeBuilder', function($http) {
	var buildUrl = function(params) {

	};
});

app.factory('$api', function($http) {
	var _http= function(url) {
		return $http({ method: 'GET', url: url, cache: true });
	};
	return {
		requestTopTen: function(attrs) {
			return _http(TOP_TEN_URL(attrs));
		}
	}
});

app.controller('ResultsController', function($scope, $routeParams, $location, $api) {

	var request;
	var params = _.pick($routeParams, 'topTenFilter');

	if (params['topTenFilter']) {
		$scope.sortable = false;
		request = $api.requestTopTen(params);
	};

	if (!request) return $location.path("/");

	request.then(function(result) {
		$scope.data = result.data;
	}, function() {
		$location.path("/");
	});
});

app.controller('MainController', function($scope) {

});

app.directive('section', function() {
	return {
		restrict: 'C',
		link: function(scope, el, attrs) {
			var sectionContent = el.find('.section-content');
			if (attrs.defaultClosed === 'closed') {
				sectionContent.hide();
			}
			el.find('.section-title').click(function() {
				sectionContent.slideToggle('slow');
			});
		}
	}
});

app.directive('searchBox', function($location) {
	var linkFn = function(scope, el, attrs) {
		scope.searchTerm = attrs.searchTerm || '';
		scope.doSearch= function() {
			if (!scope.searchTerm) return;

			var path = '#/s/' + scope.searchTerm + '/';
			var filterBy = el.find('input[type=checkbox]:checked').first();
			if (filterBy.length) {
				path += 'f/' + filterBy.val() + '/';
			}

			$location.path(path);
		};
	};

	return {
		templateUrl: 'search-box.html',
		restrict: 'C',
		link: linkFn
	}
});

app.config(function($locationProvider, $routeProvider, $compileProvider) {
	$compileProvider.urlSanitizationWhitelist(/^\s*(https?|magnet):/);
  $routeProvider.
      when('/s/:searchTerm/f/:searchFilter/o/:searchOrder/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/s/:searchTerm/f/:searchFilter/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/s/:searchTerm/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/top/f/:topTenFilter/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/', { templateUrl: 'main.html', controller: 'MainController' }).
      otherwise({redirectTo: '/'});
	$locationProvider.html5Mode(true);
});
