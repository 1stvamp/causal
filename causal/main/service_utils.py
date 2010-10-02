import httplib2
import oauth2 as oauth
from datetime import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson

from causal.main.models import RequestToken, AccessToken, UserService

PARENT_PACKAGE_NAME = 'causal.'

def user_login(service, cust_callback_url=None):
    pos = service.app.module_name.find(PARENT_PACKAGE_NAME) + len(PARENT_PACKAGE_NAME)
    callback_app_name = service.app.module_name[pos:]
    callback = cust_callback_url or reverse('causal-%s-callback' % (callback_app_name,))
    callback = "%s%s" % (service.app.oauth.callback_url_base, callback,)
    try:
        consumer = oauth.Consumer(service.app.oauth.consumer_key, service.app.oauth.consumer_secret)

        client = oauth.Client(consumer)
        resp, content = client.request(service.app.oauth.request_token_url, "GET")

        if resp['status'] != '200':
            return False

        request_token_params = dict((token.split('=') for token in content.split('&')))
        
        # fetch old token if there is one and remove it
        # so we can start from a fresh token
        rt = RequestToken.objects.filter(service=service)
        if rt:
            rt.delete()
        new_token = RequestToken()
        new_token.service = service
        new_token.oauth_token = request_token_params['oauth_token']
        new_token.oauth_token_secret = request_token_params['oauth_token_secret']
        new_token.created = datetime.now()
        new_token.save()

        redirect_url = "%s?oauth_token=%s" % (service.app.oauth.user_auth_url, request_token_params['oauth_token'],)
    except:
        return False

    # Redirect user to Twitter to authorize
    return redirect(redirect_url)

def generate_access_token(service, request_token):
    """Takes a request_token and validates it to give a valid AccessToken
    and the stores it. Should an existing token exist it will be deleted."""
    consumer = oauth.Consumer(service.app.oauth.consumer_key, service.app.oauth.consumer_secret)

    token = oauth.Token(request_token.oauth_token, request_token.oauth_token_secret)
    token.set_verifier(request_token.oauth_verify)
    client = oauth.Client(consumer, token)
    resp, content = client.request(service.app.oauth.access_token_url, "POST")

    access_token_params = dict((token.split('=') for token in content.split('&')))
    
    # check if we have existing AccessToken
    # if so delete it.
    at = AccessToken.objects.filter(service=service)
    if at:
        at.delete()
    new_at = AccessToken()
    new_at.service = service
    new_at.oauth_token = access_token_params['oauth_token']
    new_at.oauth_token_secret = access_token_params['oauth_token_secret']
    new_at.created = datetime.now()
    new_at.oauth_verify = request_token.oauth_verify
    new_at.save()
    
def get_data(service, url, disable_oauth=False):
    if disable_oauth:
        h = httplib2.Http()
        resp, content = h.request(url, "GET")
    else:
        at = AccessToken.objects.get(service=service)
        if at:
            consumer = oauth.Consumer(service.app.oauth.consumer_key, service.app.oauth.consumer_secret)
            token = oauth.Token(at.oauth_token , at.oauth_token_secret)

            client = oauth.Client(consumer, token)
            resp, content = client.request(url, "GET")
        else:
            return False
    return simplejson.loads(content)

def get_model_instance(user, module_name):
    try:
        return UserService.objects.get(user=user, app__module_name=module_name)
    except:
        return False

def get_module_name(name):
    return name.rpartition('.')[0]
