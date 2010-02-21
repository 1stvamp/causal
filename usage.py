from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template

import os

class IndexPage(webapp.RequestHandler):
    """Deals with /"""

    def get(self):
        """Handles default request."""
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))

class Login(webapp.RequestHandler):
    """Deal with logins and stuff"""

    def get(self):
        """We check if the user is logged in if not redirect"""
        user = users.get_current_user()
        if user:
            self.redirect('/')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Logout (webapp.RequestHandler):
    """Logout the user"""

    def get(self):
        self.redirect(users.create_logout_url('/'))

application = webapp.WSGIApplication(
                                     [('/', IndexPage),
                                      ('/login', Login),
                                      ('/logout', Logout)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()