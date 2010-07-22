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
class FoursquareOAuthHandler(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))

        self.redirect(do_oauth_request('foursquare', user))


class TwitterOAuthHandler(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))

        self.redirect(do_oauth_request('twitter', user))

def do_oauth_request(service, user):
    
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
    return ("%s?oauth_token=%s" % (oauth_details['user_auth_url'], 
                                         request_token_params['oauth_token']))
        
class TwitterOAuthReply(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))
        
        
        # go off to twitter
        service = 'twitter'

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
        
        token_save = OAuthAccessToken(service=service,
                                  key_name=user.nickname(),
                                  google_username=user.nickname(), 
                                  **access_token)
        token_save.save()
        
        url = oauth_details['default_api_prefix'] + '/statuses/user_timeline' + oauth_details['default_api_suffix']
        resp, content = client.request(url, "GET")
        

class FoursquareOAuthReply(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))
    
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
        
        token_save = OAuthAccessToken(service=service,
                                  key_name=user.nickname(),
                                  google_username=user.nickname(), 
                                  **access_token)
        
        token_save.save()

        
class MainHandler(RequestHandler):
    
    def get(self):
        user = users.get_current_user()
        # log user into google
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))
        twitter_details = OAUTH_APP_SETTINGS['twitter']
        template_values = {}
        consumer = oauth.Consumer(twitter_details['consumer_key'], 
                                  twitter_details['consumer_secret'])
        # fetch tokens from database
        tokens = OAuthRequestToken.all()
        tokens.filter("user = ", user.nickname())
        request_token = tokens.fetch(2)
        
        # get 200 tweets
        #oauth_details = OAUTH_APP_SETTINGS[service]
        #for i in range(0,2):
        #    url = default_api_prefix
        #    template_values['tweets'] = template_values['tweets'] + client.get('/statuses/user_timeline', count='200', page=str(i))
 	
        request_token = self.request.get('oauth_token')
        tokens = OAuthAccessToken.all()
        tokens.filter("google_username = ", user.nickname())
        tokens.filter("service = ", 'twitter')
        
        if tokens.fetch(1):
            access_token = tokens.fetch(1)[0]
            
            token = oauth.Token(access_token.oauth_token , access_token.oauth_token_secret)
            client = oauth.Client(consumer, token)
            
            url = twitter_details['default_api_prefix'] + '/statuses/user_timeline' + twitter_details['default_api_suffix']
            resp, content = client.request(url, "GET")
            template_values['tweets'] = simplejson.loads(content)
        
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))
    
application = webapp.WSGIApplication(
                                     [('/', MainHandler),
                                      ('/oauth/foursquare/login', FoursquareOAuthHandler),
                                      ('/oauth/foursquare/callback', FoursquareOAuthReply),
                                      ('/oauth/twitter/login', TwitterOAuthHandler),
                                      ('/oauth/twitter/callback', TwitterOAuthReply),
                                      ],
                                     debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()