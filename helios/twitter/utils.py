import tweepy
from datetime import datetime
from django.shortcuts import redirect

from helios.main.models import RequestToken, AccessToken

def _auth(oauth, cust_callback_url=None):
    callback = cust_callback_url or oauth.default_api_suffix
    callback = "%s%s" % (oauth.default_api_prefix, callback,)
    return tweepy.OAuthHandler(oauth.consumer_key, oauth.consumer_secret, callback)

def user_login(service, cust_callback_url=None):
    oauth = service.oauth
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
    auth = _auth(service)


    # Get access token
    access_token = AccessToken.objects.get(service=service)

    if not access_token:
        request_token = RequestToken.objects.get(service=service)
        verify_token = request.session['helios_twitter_oauth_verify_token']

        if not verify_token or not request_token:
            return False

        auth.set_request_token(request_token.oauth_token, request_token.oauth_token_secret)

        try:
            auth.get_access_token(verify_token)
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
