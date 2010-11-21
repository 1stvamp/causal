__version__ = '0.1.1'

from jogging import logging
from tweepy import TweepError
from twitter_text import TwitterText
from datetime import timedelta
from django.shortcuts import render_to_response, redirect
from causal.main.models import ServiceItem
from causal.twitter.utils import get_api, user_login
from causal.main.service_utils import get_model_instance
from causal.main.exceptions import LoggedServiceError
import re

DISPLAY_NAME = 'Twitter'
CUSTOM_FORM = False
OAUTH_FORM = True

def enable():
    """Setup and authorise the service."""
    return redirect('causal-twitter-auth')

def get_items(user, since, model_instance=None):
    items = []
    serv = model_instance or get_model_instance(user, __name__)

    api = get_api(serv)
    if not api:
        return False

    # Try to get the last ID to search from
    since_id = None
    try:
        timeline = api.search(
            "from:%s since:%s until:%s" % \
                (
                    api.me().screen_name,
                    (since-timedelta(days=1)).strftime("%Y-%m-%d"),
                    since.strftime("%Y-%m-%d"),
                ),
            rpp=1
        )
    except TweepError, e:
        if "Couldn't find Status with ID=" in e.reason:
            since_id = e.reason.split('=')[1]
    else:
        if len(timeline):
            since_id = timeline[0].id

    try:
        timeline = api.user_timeline(count=200, since_id=since_id, include_rts='true')
    except TweepError, e:
        raise LoggedServiceError(original_exception=e)
    else:
        screen_name = api.me().screen_name
        
        for status in timeline:
            item = ServiceItem()
            item.location = {}
            tt = TwitterText(status.text)
            tt.autolink.auto_link_usernames_or_lists()
            tt.autolink.auto_link_hashtags()
            item.body = unicode(tt.text)

            if re.search("http://yfrog.com/\S*", item.body) \
               or re.search("http://twitpic.com/\S*", item.body):
                item.pic_link = True
            
            item.created = status.created_at
            item.link_back = "http://twitter.com/%s/status/%s" % (screen_name, str(status.id))
            if status.geo:
                item.location['lat'] = status.geo['coordinates'][0]
                item.location['long'] = status.geo['coordinates'][1]
            item.service = serv
            item.user = user
            items.append(item)
            
    return items
