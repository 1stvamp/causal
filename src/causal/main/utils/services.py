import httplib2
import oauth2 as oauth
from datetime import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.conf import settings
from causal.main.models import RequestToken, AccessToken, UserService

PARENT_PACKAGE_NAME = 'causal.'

def user_login(service, cust_callback_url=None):
    """Authenticates to an OAuth service.
    """
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

        RequestToken.objects.create(
            oauth_token=request_token_params['oauth_token'],
            oauth_token_secret=request_token_params['oauth_token_secret'],
        )

        redirect_url = "%s?oauth_token=%s" % (service.app.oauth.user_auth_url, request_token_params['oauth_token'],)
    except:
        return False

    # Redirect user to Twitter to authorize
    return redirect(redirect_url)

def generate_access_token(service, token_url):
    """Takes a request_token and validates it to give a valid AccessToken
    and the stores it. Should an existing token exist it will be deleted.
    """
    auth_settings = get_config(service.app.module_name, 'oauth')
    consumer_key = auth_settings['consumer_key']
    consumer_secret = auth_settings['consumer_secret']
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    request_token = service.auth.request_token

    token = oauth.Token(request_token.oauth_token, request_token.oauth_token_secret)
    token.set_verifier(request_token.oauth_verify)
    client = oauth.Client(consumer, token)
    resp, content = client.request(token_url, "POST")

    access_token_params = dict((token.split('=') for token in content.split('&')))

    # Before creating a new one
    at = AccessToken.objects.create(
        oauth_token=access_token_params['oauth_token'],
        oauth_token_secret=access_token_params['oauth_token_secret'],
        oauth_verify=request_token.oauth_verify
    )
    service.auth.access_token = at
    service.auth.save()

def get_data(service, url, disable_oauth=False):
    """Helper function for retrieving JSON data from a web service, with
    optional OAuth authentication.
    """
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
    # TODO: check if we actually need this any longer, with the new
    # ServiceHandler model
    try:
        return UserService.objects.get(user=user, app__module_name=module_name)
    except Exception, e:
        return False

def settings_redirect(request):
    """Where the user is redirected to after configuring a service.
    This can be overridden in the app itself.
    """

    # Return the user back to the settings page
    return reverse('user-settings') or '/' + request.user.username

def check_is_service_id(service, module_name):
    """Check we have the correct service for the url:
    /delicious/stats/8 where 8 is the correct id otherwise redirect.
    """

    # TODO: do we still need this with ServiceHandler model?
    return service.template_name.replace('/','.') == module_name

def get_config(module_name, config_name=None):
    """Select an app specific config from settings
    """
    app_settings = getattr(settings, 'SERVICE_CONFIG', {}).get(module_name, {})
    if config_name:
        return app_settings.get(config_name, None)
    else:
        return app_settings
