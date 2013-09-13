var URL_TO_INTENT = {
	'/search/'   :   { url: '/api/search', args: ['filter', 'query', 'order'] },
	'/top/f/' :   { url: '/api/top100', args: ['filter'] }
}

var app = angular.module('app', []);

app.factory('$query', function() {
	return {
		generateSearchPath: function(params) {
			var query = params['query'];
			if (!query) throw new Error("No query param, cannot generate search URL");

			_.defaults(params, { order: 'SE', filter: 'none' });
			var result = '/search/' + query + '/';
			if (params['filter']) result += 'f/' + params['filter'] + '/';
			if (params['order']) result += 'o/' + params['order'] + '/';
			return result;
		}
	}
});

app.factory('$api', function($http) {
	var _http= function(url, params) {
		params = params || {};
		return $http({ method: 'GET', url: url, cache: true, params: params });
	};
	return {
		getDataFromRouteParams: function(path, params) {
			var startsWithUrl = _.find(_.keys(URL_TO_INTENT), function(startsWithUrl) {
				return path.indexOf(startsWithUrl) === 0;
			});
			if (!startsWithUrl) throw new Error("No Route matches an API call");

			var intentData = URL_TO_INTENT[startsWithUrl];
			return _http(
				intentData['url'],
				_.pick.apply(_, [params].concat(intentData['args']))
			);
		}
	}
});

app.controller('ResultsController', function($scope, $routeParams, $location, $api, $query) {

	$scope.orderBy = function(value) {
		return $location.path($query.generateSearchPath({
			query : $routeParams['query'],
			filter: $routeParams['filter'],
			order: value
		}));
	};

	var query = $routeParams['query']
	if (query) {
		$scope.query = query;
		$scope.filter = $routeParams['filter'];
		$scope.order = $routeParams['order'];
	}

	var _redirect = _.partial($location.path, '/');
	try {
		$api.getDataFromRouteParams($location.path(), $routeParams).then(function(result) {
			$scope.data = result.data;
		}, _redirect);
	} catch(e) {
		_redirect();
	}

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

app.directive('searchBox', function($location, $query) {
	var linkFn = function(scope, el, attrs) {
		scope.defaultQuery = scope.defaultQuery || '';
		scope.$watch('defaultFilter', function(value) {
			if (value) {
				el.find('input[value=' + value + ']').attr('checked', true);
			}
		});

		scope.doSearch= function() {
			if (!scope.defaultQuery) return;

			var filter = el.find('input[type=checkbox]:checked').first();
			$location.path($query.generateSearchPath({
				query: scope.defaultQuery,
				order: scope.defaultOrder,
				filter: filter.val() || undefined
			}));
		};
	};

	return {
		templateUrl: 'search-box.html',
		restrict: 'C',
		link: linkFn,
		scope: {
			defaultQuery: '@',
			defaultOrder: '@',
			defaultFilter: '@',
		}
	}
});

app.config(function($locationProvider, $routeProvider, $compileProvider) {
	$compileProvider.urlSanitizationWhitelist(/^\s*(https?|magnet):/);
  $routeProvider.
      when('/search/:query/f/:filter/o/:order/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/search/:query/o/:order/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/top/f/:filter/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/', { templateUrl: 'main.html' }).
      otherwise({redirectTo: '/'});
});
