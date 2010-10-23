import tweepy
from datetime import datetime
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from causal.main.models import RequestToken, AccessToken, UserService

def _auth(oauth, cust_callback_url=None):
    callback = cust_callback_url or reverse('causal-twitter-callback')
    callback = "%s%s" % (oauth.callback_url_base, callback,)
    return tweepy.OAuthHandler(oauth.consumer_key, oauth.consumer_secret, callback)

def user_login(service, cust_callback_url=None):
    """Create RequestToken to auth on user return and redirect
    user to third party url for auth."""
    oauth = service.app.oauth
    try:
        auth = _auth(oauth, cust_callback_url)

        redirect_url = auth.get_authorization_url()

        
        # check if we have an existing RequestToken
        # if so delete it.
        rt = RequestToken.objects.filter(service=service)
        if rt:
            rt.delete()
            
        # create a new requesttoken
        new_rt = RequestToken()
        new_rt.service = service
        new_rt.oauth_token = auth.request_token.key
        new_rt.oauth_token_secret = auth.request_token.secret
        new_rt.created = datetime.now()
        new_rt.save()
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

        update_attrs = {
            'oauth_token': auth.access_token.key,
            'oauth_token_secret': auth.access_token.secret,
        }
        insert_attrs = {
            'service': service,
        }
        rows = AccessToken.objects.filter(**insert_attrs).update(**update_attrs)
        if not rows:
            insert_attrs.update(update_attrs)
            insert_attrs['created'] = datetime.now()
            AccessToken.objects.create(**insert_attrs)
    else:
        auth.set_access_token(access_token.oauth_token, access_token.oauth_token_secret)

    # API instance
    return tweepy.API(auth)
