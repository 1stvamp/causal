__version__ = '0.1.1'

from tweepy import TweepError
from twitter_text import TwitterText
from datetime import timedelta
from django.shortcuts import render_to_response, redirect
from django.utils.safestring import mark_safe
from helios.main.models import UserService, ServiceItem
from helios.twitter.utils import get_api, user_login
from helios.main.service_utils import get_model_instance

display_name = 'Twitter'

def get_items(user, since, model_instance=None):
    items = []
    serv = model_instance or get_model_instance(user, __package__)

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
        print e
    else:
        for status in timeline:
            item = ServiceItem()
            tt = TwitterText(status.text)
            tt.autolink.auto_link()
            item.body = TwitterText(mark_safe(tt.text))
            item.created =status.created_at
            if status.geo:
                item.location['lat'] = status.geo[0]
                item.location['long'] = status.geo[1]
            item.service = serv
            items.append(item)
    return items
