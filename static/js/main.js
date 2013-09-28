var DEFAULT_QUERY = '';
var DEFAULT_ORDER = 'SE';
var DEFAULT_FILTER = 'none';
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

app.controller('MainController', function($scope) {
	$scope.defaultQuery = DEFAULT_QUERY;
	$scope.defaultFilter = DEFAULT_FILTER;
	$scope.defaultOrder = DEFAULT_ORDER;
});

app.controller('ResultsController', function($scope, $routeParams, $location, $api, $query) {

	$scope.orderBy = function(value) {
		return $location.path($query.generateSearchPath({
			query : $scope.query,
			filter: $scope.filter,
			order: value
		}));
	};

	var query = $routeParams['query'] || DEFAULT_QUERY;;
	$scope.query = query
	$scope.filter = query != DEFAULT_QUERY? $routeParams['filter'] : DEFAULT_FILTER;
	$scope.order = query != DEFAULT_QUERY? $routeParams['order'] : DEFAULT_ORDER;

	var _redirect = _.partial($location.path, '/');
	try {
		$scope.progressBarRun = true;
		$api.getDataFromRouteParams($location.path(), $routeParams).then(function(result) {
			$scope.progressBarRun = false;
			$scope.data = result.data;
		}, function() {
			$location.path('/');
		});
	} catch(e) {
		_redirect();
	}

});

app.directive('progressBar', function($timeout) {

	var linkFn = function(scope, el, attr) {
		scope.progressValue = 0;

		var _timeout;
		var _timeoutFn = function() {
			scope.progressValue += parseInt(scope.incrementBy);
			_timeout = $timeout(_timeoutFn, parseInt(scope.timeoutValue));
		};

		scope.$watch('run', function(status) {
			if (status) {
				_timeout = $timeout(_timeoutFn, parseInt(scope.timeoutValue));
			} else {
				$timeout.cancel(_timeout);
			}
		});
	};

	return {
		restrict: 'C',
		link: linkFn,
		scope: {
			timeoutValue: '@',
			incrementBy: '@',
			run: '='
		}
	}
});

app.directive('dropdownSelector', function($rootScope) {
	var linkFn = function(scope, el, attrs) {

		var _setValue = function(value) {
				var text = el.find('a[data-select-value="' + value + '"]').text();
				if (text) {
					scope.currentFilter = text;
					scope.filterModel = value;
					if (!$rootScope.$$phase) scope.$digest();
				}
		};

		el.find('a[data-select-value]').click(function(e) {
			e.preventDefault();
			var selectValue = $(this).data('select-value');
			_setValue(selectValue);
		});

		scope.$watch('filterModel', _setValue);
	}

	return {
		restrict: 'C',
		link: linkFn,
		scope: {
			'filterModel': '='
		}
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

		scope.doSearch= function() {
			if (!scope.defaultQuery) return;

			var filter = el.find('input[type=checkbox]:checked').first();
			$location.path($query.generateSearchPath({
				query: scope.defaultQuery,
				order: scope.defaultOrder,
				filter: scope.defaultFilter
			}));
		};
	};

	return {
		templateUrl: 'search-box.html',
		restrict: 'C',
		link: linkFn,
		scope: {
			defaultQuery: '=',
			defaultOrder: '=',
			defaultFilter: '=',
		}
	}
});

app.config(function($locationProvider, $routeProvider, $compileProvider) {
	$compileProvider.urlSanitizationWhitelist(/^\s*(https?|magnet):/);
  $routeProvider.
      when('/search/:query/f/:filter/o/:order/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/search/:query/o/:order/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/top/f/:filter/', { templateUrl: 'results.html', controller: 'ResultsController' }).
      when('/', { templateUrl: 'main.html', controller: 'MainController' }).
      otherwise({redirectTo: '/'});
});
