from causal.main.models import ServiceItem
from causal.main.service_utils import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError
from django.shortcuts import render_to_response, redirect
from causal.main.models import AccessToken, ServiceItem
from dateutil import parser
from datetime import datetime, timedelta
import feedparser

DISPLAY_NAME = 'Delicious'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    
    at = AccessToken.objects.get(service=serv)
    url = 'http://feeds.delicious.com/v2/rss/%s?count=100' % (at.username,)
    feed = feedparser.parse(url)
    
    return _convert_feed(feed, serv, user)
    
def _convert_feed(feed, serv, user):
    items = []
    for entry in feed.entries:
        item = ServiceItem()
        item.title = entry.title
        item.body = entry.link
        updated = parser.parse(entry.updated)
        updated = (updated - updated.utcoffset()).replace(tzinfo=None)
        item.created = updated
        item.link_back = entry.id
        item.service = serv
        item.user = user
        items.append(item)
    
    return items
