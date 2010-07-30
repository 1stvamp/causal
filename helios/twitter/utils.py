import tweepy
from datetime import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from helios.main.models import RequestToken, AccessToken, UserService

def _auth(oauth, cust_callback_url=None):
    callback = cust_callback_url or reverse('helios-twitter-callback')
    callback = "%s%s" % (oauth.callback_url_base, callback,)
    return tweepy.OAuthHandler(oauth.consumer_key, oauth.consumer_secret, callback)

def user_login(service, cust_callback_url=None):
    oauth = service.app.oauth
    try:
        auth = _auth(oauth, cust_callback_url)

        redirect_url = auth.get_authorization_url()

        RequestToken.objects.create(
            service=service,
            oauth_token=auth.request_token.key,
            oauth_token_secret=auth.request_token.secret,
            created=datetime.now()
        )
    except tweepy.TweepError:
        return False

    # Redirect user to Twitter to authorize
    return redirect(redirect_url)


def get_api(service):
    auth = _auth(service.app.oauth)

    # Get access token
    try:
        access_token = AccessToken.objects.get(service=service)
    except AccessToken.DoesNotExist:
        try:
            request_token = RequestToken.objects.get(service=service)
        except RequestToken.DoesNotExist:
            return False

        auth.set_request_token(request_token.oauth_token, request_token.oauth_token_secret)

        try:
            auth.get_access_token(request_token.oauth_verify)
        except tweepy.TweepError:
            return False

        AccessToken.objects.create(
            service=service,
            oauth_token=auth.access_token.key,
            oauth_token_secret=auth.access_token.secret,
            created=datetime.now()
        )
    else:
        auth.set_access_token(access_token.oauth_token, access_token.oauth_token_secret)

    # API instance
    return tweepy.API(auth)

def get_model_instance(user):
    return UserService.objects.get(user=user, app__module_name=__package__)
