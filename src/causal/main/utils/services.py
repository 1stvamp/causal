import httplib2
import oauth2 as oauth
from datetime import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.conf import settings
from django.contrib.sites.models import Site
from causal.main.models import RequestToken, AccessToken, UserService, OAuth

def user_login(service, cust_callback_url=None):
    """Authenticates to an OAuth service.
    """
    current_site = Site.objects.get(id=settings.SITE_ID)
    auth_settings = get_config(service.app.module_name, 'oauth')
    callback = cust_callback_url or reverse(service.app.module_name.replace('.', '-'))
    callback = "http://%s%s" % (current_site.domain, callback,)
    try:
        consumer = oauth.Consumer(auth_settings['consumer_key'], auth_settings['consumer_secret'])

        client = oauth.Client(consumer)
        resp, content = client.request("https://graph.facebook.com/oauth/authorize", "GET")

        if resp['status'] != '200':
            return False

        request_token_params = dict((token.split('=') for token in content.split('&')))

        rt = RequestToken.objects.create(
            oauth_token=request_token_params['oauth_token'],
            oauth_token_secret=request_token_params['oauth_token_secret'],
        )
        if not service.auth:
            auth_handler = service.auth = OAuth()
        else:
            auth_handler = service.auth
        auth_handler.request_token = rt
        auth_handler.save()
        if not service.auth:
            service.auth = auth_handler
            service.save()

        redirect_url = "%s?oauth_token=%s" % (
            "https://graph.facebook.com/oauth/access_token",
            request_token_params['oauth_token']
        )
    except:
        return False

    # Redirect user to Twitter to authorize
    return redirect(redirect_url)

def generate_access_token(service, token_url):
    """Takes a request_token and validates it to give a valid AccessToken
    and the stores it. Should an existing token exist it will be deleted.
    """
    auth_settings = get_config(service.app.module_name, 'oauth')
    consumer = oauth.Consumer(auth_settings['consumer_key'], auth_settings['consumer_secret'])
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

    auth_settings = get_config(service.app.module_name, 'oauth')
    if disable_oauth:
        h = httplib2.Http()
        resp, content = h.request(url, "GET")
    else:
        at = service.auth.access_token
        if at:
            consumer = oauth.Consumer(auth_settings['consumer_key'], auth_settings['consumer_secret'])
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
    return reverse('user-settings') or '/%s' % (request.user.username,)

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
