describe('Italian Bay tests', function() {
	var _api;
	var _httpBackend;
	var _query;

	beforeEach(module('app'));

	beforeEach(inject(function($query, $api, $httpBackend) {
		_query = $query;
		_api = $api;
		_httpBackend = $httpBackend;
	}));

	it('Should be able to get Top 100', function() {
		_httpBackend.expectGET('/api/top100?filter=audio').respond([]);
		_api.getDataFromRouteParams('/top/f/audio/', {
			filter: 'audio'
		});

		_httpBackend.verifyNoOutstandingExpectation();
	});

	it('Should raise an exception if data is missing', function() {
		expect(_.partial(_api.getDataFromRouteParams, '/wierd/api/', {}))
			.toThrow("No Route matches an API call");
	});

	it('Should be able to get search with query, filter and order', function() {
		[
			'/api/search?q=Hello%20World', // Only query
			'/api/search?filter=video&q=Hello%20World', // Query and filter
			'/api/search?filter=video&order=SE&q=Hello%20World', // Query, filter and order
		].forEach(function(api) {
			_httpBackend.expectGET(api).respond([]);
		});

		[
			{ url: '/search/Hello%20World/', q: 'Hello World' }, // Only query
			{ url: '/search/Hello%20World/f/video/', q: 'Hello World', filter: 'video' }, // Query and filter
			{ url: '/search/Hello%20World/f/video/o/SE/', q: 'Hello World', filter: 'video', order: 'SE' } // Query, filter and order
		].forEach(function(params) {
			var url = params['url']
			delete params['url']; 
			_api.getDataFromRouteParams(url, params);
		});

		_httpBackend.verifyNoOutstandingExpectation();
		
	});

	it("Should throw an exception if no query is provided", function() {
		expect(_.partial(_query.generateSearchPath, {}))
			.toThrow("No query param, cannot generate search URL");
	});

	it("Should be able to generate a query with order and filter", function() {

		var path = _query.generateSearchPath({ query: 'Hello World' });
		expect(path).toEqual('/search/Hello%20World/');

		var path = _query.generateSearchPath({ query: 'ubuntu', order: 'LE' });
		expect(path).toEqual('/search/ubuntu/o/LE/');

		var path = _query.generateSearchPath({ query: 'ubuntu', filter: 'application' });
		expect(path).toEqual('/search/ubuntu/f/application/');

		var path = _query.generateSearchPath({ query: 'ubuntu', filter: 'application', order: 'SE' });
		expect(path).toEqual('/search/ubuntu/f/application/o/SE/');
	});

});

describe('Filter Dropdown tests', function() {
	var el, scope;

	beforeEach(module('app'));

	beforeEach(inject(function($rootScope, $compile) {
		elm = angular.element(
				'<span class="input-group-btn dropdown-selector" filter-model="currentFilter" >' + 
					'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">{{ currentFilter }}<span class="caret"></span></button>' + 
					'<ul class="dropdown-menu pull-right">' + 
						'<li><a data-select-value="none" href="#">No Filter</a></li>' + 
						'<li><a data-select-value="audio" href="#">Audio</a></li>' + 
						'<li><a data-select-value="video" href="#">Video</a></li>' + 
					'</ul>' + 
				'</span>'
			);

			scope = $rootScope;
			$compile(elm)(scope);
	}));

	it('Should be able to get the default element', function() {
		scope.currentFilter = "audio";
		scope.$digest();
		expect(elm.find('button').text()).toEqual('Audio');
	});

	it('Should be able to set the default element', function() {
		scope.currentFilter = "audio";
		scope.$digest();

		elm.find('a[data-select-value="none"]').click();
		scope.$digest();

		expect(scope.currentFilter).toEqual('none');
		expect(elm.find('button').text()).toEqual('No Filter');
	});

});

describe('Progress bar tests', function() {
	var el, scope, _timeout;

	beforeEach(module('app'));

	beforeEach(inject(function($rootScope, $compile, $timeout) {
		elm = angular.element('<span increment-by="3" timeout-value="500" run="runState" class="progress-bar">');
			_timeout = $timeout;
			scope = $rootScope;
			$compile(elm)(scope);
	}));

	it("should start from 0", function() {
		expect(elm.scope().progressValue).toEqual(0);
	});

	it("should start progressing", function() {
		expect(elm.scope().progressValue).toEqual(0);

		scope.runState = true;
		scope.$digest();
		_timeout.flush();

		expect(elm.scope().progressValue).toEqual(3);

	});

});
