"""Handles user accessable urls for http://twitter.com service.
We ask for read only permissions using full blown oauth2.
"""

import re
import logging
import tweepy
from causal.main.decorators import can_view_service
from causal.main.models import UserService, RequestToken, ServiceApp
from causal.main.utils import get_module_name
from causal.main.utils.services import get_model_instance, \
     generate_access_token, settings_redirect, check_is_service_id
from causal.main.utils.views import render
from causal.twitter.service import get_items
from causal.twitter.utils import _auth, user_login
from datetime import date, timedelta
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict

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

    # Mark as setup completed
    service.setup = True

    # test if service is protected on twitter's side
    # if so mark it
    service_auth = _auth(service.app.oauth)
    user = tweepy.API(service_auth).get_user('twitter')
    service.public = False
    if not user.protected:
        service.public = True

    service.save()

    request_token.delete()
    return HttpResponseRedirect(settings_redirect(request))

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """Prepare a oauth request by saving a record locally ready for the
    redirect from twitter."""
    request.session['causal_twitter_oauth_return_url'] = \
           request.GET.get('HTTP_REFERER', None)
    service = get_model_instance(request.user, MODULE_NAME)
    if not service:
        app = ServiceApp.objects.get(module_name=MODULE_NAME)
        service = UserService(user=request.user, app=app)
        service.save()
    else:
        logging.error('Service not found')
    return user_login(service)

@can_view_service
def stats(request, service_id):
    """Create up some stats."""
    service = get_object_or_404(UserService, pk=service_id)
    if check_is_service_id(service, MODULE_NAME):
        # get tweets
        tweets = get_items(request.user, date.today() - timedelta(days=7), service)
        retweets = 0
        template_values = {}

        # retweet ratio
        # who you tweet the most
        ats = {}

        # to store a break down of tweets per day
        days = {}
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

                if days.has_key(tweet.created.strftime('%d')):
                    days[tweet.created.strftime('%d')] = \
                        days[tweet.created.strftime('%d')] + 1
                else:
                    days[tweet.created.strftime('%d')] = 1

            template_values['retweets'] = retweets
            template_values['non_retweets'] = len(tweets) - retweets
            template_values['total_tweets'] = len(tweets)
            template_values['tweets'] = tweets
            template_values['tweets_per_day'] = \
                           sorted(days.iteritems(), key=lambda (k, v) : (v, k))
            template_values['max_tweets_per_day'] = \
                           template_values['tweets_per_day'][-1][1]

            days = {}

            # tweets per day

            # order by value and reverse to put most popular at the top
            template_values['atters'] = SortedDict(
                sorted(ats.items(), reverse=True, key=lambda x: x[1]))
        return render(
            request,
            template_values,
            service.template_name + '/stats.html'
        )
    else:
        return redirect('/%s' %(request.user.username))
