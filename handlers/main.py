
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from settings import TEMPLATE_PATH
from libs import PirateBayAPI

from urllib import url2pathname

# GET /
class RootHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render(TEMPLATE_PATH + 'index.html', {}))
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
class RequestResultsForValueHandler(webapp.RequestHandler):
    def get(self, value, filter= 'none', orderby= 'SE'):
                
         # Check if values have been passed, if not redirect to root
         if value == "":
             return self.redirect('/')
         
         # Decode value parameter
         value = url2pathname(value)
         
         # Render Response
         results = PirateBayAPI.requestResultsForValue(value=value, filter=filter, orderBy=orderby)
         base_url = self.request.host_url + '/s/%s/f/%s/' % (value, filter)
         self.response.out.write(template.render(TEMPLATE_PATH + 'search-results.html', {'results' : results, 'title' : "Results for: %s" % value, 'sortable' : True, 'base_url' : base_url}))

# GET /requestResultsforTop100?filter=video
class RequestResultsforTop100(webapp.RequestHandler):
    def get(self, filter= 'none'):
        results = PirateBayAPI.requestResultsforTop100(filter=filter)
        
        title = "Top 100"
        if filter != 'none': title += " in %s" % filter
        
        self.response.out.write(template.render(TEMPLATE_PATH + 'search-results.html', {'results' : results, 'title' : title, 'sortable' : False}))

# GET /requestResultsforRecentUploads
class RequestResultsforRecentUploads(webapp.RequestHandler):
    def get(self):
        results = PirateBayAPI.requestResultsforRecentUploads()
        self.response.out.write(template.render(TEMPLATE_PATH + 'search-results.html', {'results' : results, 'title' : 'Recent uploads', 'sortable' : False}))

# END TORRENT SEARCH HANDLERS

def main():
    application = webapp.WSGIApplication([
    ('/s/(.*)/f/(.*)/o/(.*)/', RequestResultsForValueHandler), ('/s/(.*)/f/(.*)/', RequestResultsForValueHandler), ('/s/(.*)/', RequestResultsForValueHandler),
    ('/top/f/(.*)/', RequestResultsforTop100), ('/top/', RequestResultsforTop100),
    ('/requestTorrentForResultURL', RequestTorrentForResultURL), ('/requestResultsforRecentUploads', RequestResultsforRecentUploads),
    ('/', RootHandler)],
    debug=False)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
