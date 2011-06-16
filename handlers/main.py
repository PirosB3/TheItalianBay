
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from settings import TEMPLATE_PATH
from libs.PirateBayAPI import PirateBayAPI

# GET /
class RootHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render(TEMPLATE_PATH + 'index.html', {}))

# GET /requestResultsForValue?value=spider+man&filter=video
class RequestResultsForValueHandler(webapp.RequestHandler):
    def get(self):
        
        # Check if values have been passed, if not redirect to root
        value = self.request.get('value')
        if value == "":
            return self.redirect('/')
            
        # Check if filters have been applied
        filter = self.request.get('filter')
        if filter == '':
            filter = 'none'
            
        # Render Response
        results = PirateBayAPI().requestResultsForValue(value=value, filter=filter)
        self.response.out.write(template.render(TEMPLATE_PATH + 'search-results.html', {'results' : results, 'original_query' : value}))

# GET /requestResultsforTop100?filter=video
class RequestResultsforTop100(webapp.RequestHandler):
    def get(self):
        filter = self.request.get('filter')
        if filter == '':
            filter = 'none'
        
        results = PirateBayAPI().requestResultsforTop100(filter=filter)
        self.response.out.write(template.render(TEMPLATE_PATH + 'search-results.html', {'results' : results, 'original_query' : ''}))

# GET /requestTorrentForResultURL?url=/torrent/5945000/Call.of.Duty.Black.Ops-SKIDROW-[tracker.BTARENA.org].iso
class RequestTorrentForResultURL(webapp.RequestHandler):
    def get(self):
        url = self.request.get('url')
        if url == '':
            return self.redirect('/')
        
        fileURL = PirateBayAPI().requestTorrentForResultURL(url)
        self.redirect(fileURL['torrent_url'])

def main():
    application = webapp.WSGIApplication([('/', RootHandler), ('/requestResultsForValue', RequestResultsForValueHandler), ('/requestResultsforTop100', RequestResultsforTop100), ('/requestTorrentForResultURL', RequestTorrentForResultURL)],
                                         debug=False)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
