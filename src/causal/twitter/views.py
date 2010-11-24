from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from causal.main.models import UserService, RequestToken, OAuthSetting, ServiceApp
from causal.twitter.utils import user_login
from causal.main.service_utils import get_model_instance, generate_access_token, get_module_name
from causal.twitter.service import get_items
from datetime import date, timedelta
from django.utils.datastructures import SortedDict
import re
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from causal.main.decorators import can_view_service
from django.http import HttpResponseRedirect

from causal.twitter.utils import _auth
import tweepy
# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    """Take incoming request and validate it to create a valid AccessToken."""
    service = get_model_instance(request.user, MODULE_NAME)
    request_token = RequestToken.objects.get(service=service)
    request_token.oauth_verify = request.GET.get('oauth_verifier')
    request_token.save()
    generate_access_token(service, request_token)
    return_url = request.session.get('causal_twitter_oauth_return_url', None) or '/' + request.user.username
    # Mark as setup completed
    service.setup = True
    
    # test if service is protected on twitter's side
    # if so mark it
    auth = _auth(service.app.oauth)
    user = tweepy.API(auth).get_user('twitter')
    service.public = False
    if not user.protected:
        service.public = True
    
    service.save()
    
    request_token.delete()
    return HttpResponseRedirect(return_url)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """Prepare a oauth request by saving a record locally ready for the
    redirect from twitter."""
    request.session['causal_twitter_oauth_return_url'] = request.GET.get('HTTP_REFERER', None)
    service = get_model_instance(request.user, MODULE_NAME)
    if not service:
        app = ServiceApp.objects.get(module_name=MODULE_NAME)
        service = UserService(user=request.user, app=app)
        service.save()
    return user_login(service)

@can_view_service
def stats(request, service_id):
    """Create up some stats."""
    service = get_object_or_404(UserService, pk=service_id)

    # get tweets
    tweets = get_items(request.user, date.today() - timedelta(days=7), service)
    retweets = 0
    template_values = {}

    # retweet ratio
    # who you tweet the most
    ats = {}
    if tweets:
        for tweet in tweets:
            if tweet.has_location():
                template_values['tweet_centre'] = tweet
            if re.match('RT', tweet.body):
                retweets = retweets + 1
            else:
                atteds = re.findall('@[\w]*', tweet.body)
                for i in atteds:
                    if ats.has_key(i):
                        ats[i] = ats[i] + 1
                    else:
                        ats[i] = 1

        template_values['retweets'] = retweets
        template_values['non_retweets'] = len(tweets) - retweets
        template_values['total_tweets'] = len(tweets)
        template_values['tweets'] = tweets
        
        # order by value and reverse to put most popular at the top
        template_values['atters'] = SortedDict(sorted(ats.items(), reverse=True, key=lambda x: x[1]))
    return render_to_response(
        service.template_name + '/stats.html',
        template_values,
        context_instance=RequestContext(request)
    )

