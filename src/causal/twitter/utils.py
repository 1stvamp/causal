import tweepy
from datetime import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from causal.main.utils.services import get_config

from causal.main.models import OAuth, RequestToken, AccessToken, UserService

auth_settings = get_config('causal.twitter', 'oauth')
if not auth_settings:
    raise Exception('Missing Twitter OAuth config in settings module')

def _oauth(cust_callback_url=None):
    current_site = Site.objects.get(id=settings.SITE_ID)
    callback = cust_callback_url or reverse('causal-twitter-callback')
    callback = "http://%s%s" % (current_site.domain, callback,)
    return tweepy.OAuthHandler(
        auth_settings['consumer_key'],
        auth_settings['consumer_secret'],
        callback
    )

def user_login(service, cust_callback_url=None):
    """Create RequestToken to auth on user return and redirect
    user to third party url for auth."""
    try:
        oauth = _oauth(cust_callback_url)
        redirect_url = oauth.get_authorization_url()

        # Make sure we have an auth container
        if not service.auth:
            auth_handler = OAuth()
        else:
            auth_handler = service.auth

        # Create a new requesttoken
        new_rt = RequestToken()
        new_rt.oauth_token = oauth.request_token.key
        new_rt.oauth_token_secret = oauth.request_token.secret
        new_rt.save()
        auth_handler.request_token = new_rt
        auth_handler.save()
        if not service.auth:
            service.auth = auth_handler
            service.save()
    except tweepy.TweepError:
        return False

    # Redirect user to Twitter to authorize
    return redirect(redirect_url)

def get_api(service):
    oauth = _oauth()

    # Have we authenticated at all?
    if not service.auth:
        return False

    # Get access token
    if not service.auth.access_token:
        if not service.auth.request_token:
            return False

        oauth.set_request_token(
            service.auth.request_token.oauth_token,
            service.auth.request_token.oauth_token_secret
        )

        try:
            oauth.get_access_token(service.auth.request_token.oauth_verify)
        except tweepy.TweepError:
            return False

        at = AccessToken.objects.get_or_create(
            oauth_token=auth.access_token.key,
            oauth_token_secret=auth.access_token.secret
        )
        service.auth.access_token = at
        service.auth.save()
    else:
        oauth.set_access_token(
            service.auth.access_token.oauth_token,
            service.auth.access_token.oauth_token_secret
        )

    # API instance
    return tweepy.API(oauth)

def get_user(service):
    service_auth = _oauth(service.auth)
    return tweepy.API(service_auth).get_user('twitter')
