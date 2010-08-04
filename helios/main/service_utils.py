import httplib2
import oauth2 as oauth
from datetime import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson

from helios.main.models import RequestToken, AccessToken, UserService

def user_login(service, cust_callback_url=None):
    helios_package_name = 'helios.'
    pos = service.app.module_name.find(helios_package_name) + len(helios_package_name)
    callback_app_name = service.app.module_name[pos:]
    callback = cust_callback_url or reverse('helios-%s-callback' % (callback_app_name,))
    callback = "%s%s" % (service.app.oauth.callback_url_base, callback,)
    try:
        consumer = oauth.Consumer(service.app.oauth.consumer_key, service.app.oauth.consumer_secret)

        client = oauth.Client(consumer)
        resp, content = client.request(service.app.oauth.request_token_url, "GET")

        if resp['status'] != '200':
            return False

        request_token_params = dict((token.split('=') for token in content.split('&')))

        update_attrs = {
            'oauth_token': request_token_params['oauth_token'],
            'oauth_token_secret': request_token_params['oauth_token_secret'],
        }
        insert_attrs = {
            'service': service,
        }
        rows = RequestToken.objects.filter(**insert_attrs).update(**update_attrs)
        if not rows:
            insert_attrs.update(update_attrs)
            insert_attrs['created'] = datetime.now()
            RequestToken.objects.create(**insert_attrs)

        redirect_url = "%s?oauth_token=%s" % (service.app.oauth.user_auth_url, request_token_params['oauth_token'],)
    except:
        return False

    # Redirect user to Twitter to authorize
    return redirect(redirect_url)

def generate_access_token(service, request_token):
    consumer = oauth.Consumer(service.app.oauth.consumer_key, service.app.oauth.consumer_secret)

    token = oauth.Token(request_token.oauth_token, request_token.oauth_token_secret)
    client = oauth.Client(consumer, token)
    resp, content = client.request(service.app.oauth.access_token_url, "POST")

    access_token_params = dict((token.split('=') for token in content.split('&')))

    update_attrs = {
        'oauth_token': access_token_params['oauth_token'],
        'oauth_token_secret': access_token_params['oauth_token_secret'],
    }
    insert_attrs = {
        'service': service,
    }
    rows = AccessToken.objects.filter(**insert_attrs).update(**update_attrs)
    if not rows:
        insert_attrs.update(update_attrs)
        insert_attrs['created'] = datetime.now()
        AccessToken.objects.create(**insert_attrs)

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
    return UserService.objects.get(user=user, app__module_name=module_name)

