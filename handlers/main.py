
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
        if value is '':
            self.redirect('/')
            
        # Check if filters have been applied
        filter = self.request.get('filter')
        if filter is '':
            filter = 'none'
            
        # Render Response
        results = PirateBayAPI().requestResultsForValue(value=value, filter=filter)
        self.response.out.write(results)

def main():
    application = webapp.WSGIApplication([('/', RootHandler), ('/requestResultsForValue', RequestResultsForValueHandler)],
                                         debug=False)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
