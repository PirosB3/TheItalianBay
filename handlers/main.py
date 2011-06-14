
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from settings import TEMPLATE_PATH

# GET /
class RootHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render(TEMPLATE_PATH + 'index.html', {}))


def main():
    application = webapp.WSGIApplication([('/', RootHandler)],
                                         debug=False)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
