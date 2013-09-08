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
