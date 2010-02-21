from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template

import os

class Reading(db.Model):
    user = db.UserProperty()
    postcode = db.StringProperty(multiline=True)
    electric = db.StringProperty()
    gas = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class IndexPage(webapp.RequestHandler):
    """Deals with /"""

    def get(self):
        """Handles default request. Display a select sample."""
        user = users.get_current_user()

        # get a select of people to display
        # soon this will be ppl nearby
        readings = Reading.gql("ORDER BY date DESC LIMIT 10")

        if readings.count() == 0:
            readings = None
        template_values = {'user' : user,
                           'readings' : readings}
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        """Log their postcode and cost"""

        user = users.get_current_user()

        if user:
            postcode = self.request.get('postcode')
            electric = self.request.get('electric')
            gas = self.request.get('gas')
            reading = Reading()
            reading.user = user
            reading.postcode = postcode
            reading.gas = gas
            reading.electric = electric
            reading.put()
            template_values = {}
            path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
            self.response.out.write(template.render(path, template_values))

        else:
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
        """Log them out and back to the front page."""
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