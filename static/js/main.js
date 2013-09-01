var TOP_TEN_URL = _.template('/api/top/f/<%= topTenFilter %>/');

var app = angular.module('app', []);

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


app.config(function($locationProvider, $routeProvider, $compileProvider) {
	$compileProvider.urlSanitizationWhitelist(/^\s*(https?|magnet):/);
  $routeProvider.
      when('/top/f/:topTenFilter/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/', { templateUrl: 'main.html', controller: 'MainController' }).
      otherwise({redirectTo: '/'});
});
