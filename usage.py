from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os
import logging
import urlparse
import oauth2 as oauth

from django.utils import simplejson

from google.appengine.api.urlfetch import fetch as urlfetch, GET, POST
from google.appengine.ext import db
from google.appengine.ext.webapp import RequestHandler, WSGIApplication
from models import OAuthAccessToken, OAuthRequestToken

OAUTH_APP_SETTINGS = {

    'twitter': {

        'consumer_key': 'hX6Da559MW6IIo0yVAcRrQ',
        'consumer_secret': 'AHEh5NwOfIWL1K32xmqHQdTrztJnvayxzzy81BPTdbY',

        'request_token_url': 'https://twitter.com/oauth/request_token',
        'access_token_url': 'https://twitter.com/oauth/access_token',
        'user_auth_url': 'http://twitter.com/oauth/authorize',

        'default_api_prefix': 'http://twitter.com',
        'default_api_suffix': '.json',

        },

    'foursquare': {

        'consumer_key': 'WZG3BFLERY1FOCNVA2D5NNZZ3IG0MR4DOYHA4BQAQT40PWX5',
        'consumer_secret': 'DI1SYWTW4VK53UEJGNCJ2VGTWGMCVPV5NGMYZ20YXMJD5YQ3',

        'request_token_url': 'http://foursquare.com/oauth/request_token',
        'access_token_url': 'https://foursquare.com/oauth/access_token',
        'user_auth_url': 'http://foursquare.com/oauth/authorize',

        'default_api_prefix': 'http://foursquare.com',
        'default_api_suffix': '.json',

        },
    }

class OAuthHandler(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))
        if 'twitter' in self.get_url():
            # go off to twitter
            self.do_oauth_request('twitter', user)
        
        if 'foursquare' in self.get_url():
            # go off to foursquare
            pass

    def do_oauth_request(self, service, user):
        
        oauth_details = OAUTH_APP_SETTINGS[service]
        consumer = oauth.Consumer(oauth_details['consumer_key'], 
                                  oauth_details['consumer_secret'])
        
        client = oauth.Client(consumer)
        resp, content = client.request(oauth_details['request_token_url'], "GET")
        
        if resp['status'] != '200':
            print "fail"
        
        request_token_params = dict((token.split('=') for token in content.split('&')))
        
        token = OAuthRequestToken(service=service,
                                  key_name=user.nickname(),
                                  user=user.nickname(), 
                                  **request_token_params)
        token.save()
        self.redirect("%s?oauth_token=%s" % (oauth_details['user_auth_url'], 
                                             request_token_params['oauth_token']))
        
class OAuthReply(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))
        
        if 'twitter' in self.get_url():
            # go off to twitter
            service = 'twitter'
        
        if 'foursquare' in self.get_url():
            # go off to foursquare
            service = 'foursquare'

        oauth_details = OAUTH_APP_SETTINGS[service]
        
        # fetch token details
        request_token = self.request.get('oauth_token')
        tokens = OAuthRequestToken.all()
        tokens.filter("oauth_token = ", request_token)
        request_token = tokens.fetch(1)[0]
        
        # creat consumer
        consumer = oauth.Consumer(oauth_details['consumer_key'], 
                                  oauth_details['consumer_secret'])
        
        
        token = oauth.Token(request_token.oauth_token, request_token.oauth_token_secret)
        
        client = oauth.Client(consumer, token)
        resp, content = client.request(oauth_details['access_token_url'], "POST")
        
        access_token = dict((token.split('=') for token in content.split('&')))
        
        token = oauth.Token(access_token['oauth_token'] , access_token['oauth_token_secret'])
        client = oauth.Client(consumer, token)
        url = 'http://twitter.com/account/verify_credentials.xml'
        resp, content = client.request(url, "GET")
        
        print content
        
        token_save = OAuthAccessToken(service=service,
                                  key_name=user.nickname(),
                                  user=user.nickname(), 
                                  **access_token)
        
        #instance.trusted_request_token = access_token['oauth_token']
        #instance.trusted_request_token_secret = access_token['oauth_token_secret']

class MainHandler(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))
        
        template_values = {}
        
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))
    
application = webapp.WSGIApplication(
                                     [('/', MainHandler),
                                      ('/oauth/twitter/login', OAuthHandler),
                                      ('/oauth/twitter/callback', OAuthReply),
                                      ('/oauth/foursquare/login', OAuthHandler),
                                      ('/oauth/foursquare/callback', OAuthReply),
                                      ],
                                     debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()