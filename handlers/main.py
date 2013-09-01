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

def _render_template(template_name, args= {}):
    template = JINJA_ENVIRONMENT.get_template(template_name)
    return template.render(args)


# GET /
class RootHandler(webapp2.RequestHandler):
    def get(self):
        print webapp2.__file__
        self.response.out.write(_render_template('index.html'))
    def post(self):
        """POSTing on root I can redirect to a pretty url without having to add trouble javascript on the client side"""
        
        # Get type of request, if not present redirect to root
        method = self.request.get('method')
        if method == "":
            return self.redirect('/')
        
        # POST / method=RequestResultsForValueHandler
        if method == 'RequestResultsForValueHandler':
            value = self.request.get('value')
            filter = self.request.get('filter')
        
            # Check necessary filters have been applied
            if value == "" or method == "":
                return self.redirect('/')
            if filter == '':
                filter = 'none'
            
            # redirect to pretty url
            self.redirect('/s/%s/f/%s/' % (value, filter))
        

# TORRENT SEARCH HANDLERS

# GET /requestResultsForValue?value=spider+man&filter=video
class RequestResultsForValueHandler(webapp2.RequestHandler):
    def get(self, value, filter= 'none', orderby= 'SE'):
         
         # Check if values have been passed, if not redirect to root
         if value == "":
             return self.redirect('/')
         
         # Decode value parameter
         value = url2pathname(value)
         
         # Render Response
         results = PirateBayAPI.requestResultsForValue(value=value, filter_name=filter, orderBy=orderby)
         base_url = self.request.host_url + '/s/%s/f/%s/' % (value, filter)
         self.response.out.write(_render_template('search-results.html'), {
             'results' : results,
             'title' : "Results for: %s" % value,
             'sortable' : True,
             'base_url' : base_url
         })

# GET /requestResultsforTop100?filter=video
class RequestResultsforTop100(webapp2.RequestHandler):
    def get(self, filter= 'none'):
        results = PirateBayAPI.requestResultsforTop100(filter_name=filter)
        
        title = "Top 100"
        if filter != 'none': title += " in %s" % filter
        
        self.response.out.write(_render_template('search-results.html', {
             'results' : results,
             'title' : title,
             'sortable' : False
        }))


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

# GET /requestResultsforRecentUploads
class RequestResultsforRecentUploads(webapp2.RequestHandler):
    def get(self):
        results = PirateBayAPI.requestResultsforRecentUploads()
        self.response.out.write(_render_template('search-results.html'), {
            'results' : results,
            'title' : 'Recent uploads',
            'sortable' : False
        })

# If running locally, proxy requests to GAE
if DEBUG_ENABLED:
    from google.appengine.ext.remote_api import remote_api_stub
    remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', 
        lambda: (os.environ['TIB_USERNAME'], os.environ['TIB_PASSWORD']), 'theitalianbay.appspot.com')

# END TORRENT SEARCH HANDLERS
app= webapp2.WSGIApplication([
        ('/tasks/cache_warming', CacheWarmingHandler),
        ('/s/(.*)/f/(.*)/o/(.*)/', RequestResultsForValueHandler),
        ('/s/(.*)/f/(.*)/', RequestResultsForValueHandler),
        ('/s/(.*)/', RequestResultsForValueHandler),
        ('/top/f/(.*)/', RequestResultsforTop100),
        ('/top/', RequestResultsforTop100),
        ('/', RootHandler)
    ],
    debug= DEBUG_ENABLED
)
