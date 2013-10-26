import os
import functools
import json
import logging

import webapp2
import jinja2

from urllib import url2pathname
from libs import PirateBayAPI

DEBUG_ENABLED = 'GAE_DEBUG' in os.environ
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates/')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
    extensions=['jinja2.ext.autoescape'])

def json_response(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))
    return wrapper


class RootHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.out.write(template.render())

# TORRENT SEARCH HANDLERS
# GET /requestResultsForValue?value=spider+man&filter=video
class RequestResultsForValueHandler(webapp2.RequestHandler):

    @json_response
    def get(self):

        value = self.request.get('query', None)
        filter_name = self.request.get('filter', None)
        order_by = self.request.get('order', None)

        if not value:
            return self.redirect('/')
         
        return PirateBayAPI.requestResultsForValue(value=url2pathname(value),
           filter_name=filter_name, orderBy=order_by)


# GET /requestResultsforTop100?filter=video
class RequestResultsforTop100(webapp2.RequestHandler):

    @json_response
    def get(self):
        filter_name = self.request.get('filter', 'none')
        return PirateBayAPI.requestResultsforTop100(filter_name=filter_name)


# GET /requestResultsforRecentUploads
class RequestResultsforRecentUploads(webapp2.RequestHandler):

    @json_response
    def get(self):
        return PirateBayAPI.requestResultsforRecentUploads()


# GET /tasks/cache_warming
class CacheWarmingHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("Cache warming started.")
        res = {}
        warm_for_top_100 = functools.partial(
            PirateBayAPI.requestResultsforTop100,
            cache_warming=True
        )
        for filter_name in PirateBayAPI.FILTER_BY.keys():
            try:
                warm_for_top_100(filter_name=filter_name)
                res[filter_name] = 'OK'
            except Exception as e:
                res[filter_name] = str(e)
        logging.info("Cache warming ended.")
        self.response.out.write(json.dumps(res))


# If running locally, proxy requests to GAE
if DEBUG_ENABLED:
    from google.appengine.ext.remote_api import remote_api_stub
    remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', 
        lambda: (os.environ['TIB_USERNAME'], os.environ['TIB_PASSWORD']), 'theitalianbay.appspot.com')

# END TORRENT SEARCH HANDLERS
app= webapp2.WSGIApplication([
        ('/api/cache_warm', CacheWarmingHandler),
        ('/api/search', RequestResultsForValueHandler),
        ('/api/top100', RequestResultsforTop100),
        ('/api/top/', RequestResultsforTop100)
    ],
    debug=DEBUG_ENABLED
)
