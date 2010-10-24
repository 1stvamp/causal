import time
import feedparser
from dateutil import parser
from datetime import datetime
from causal.main.models import AccessToken, ServiceItem
from causal.main.service_utils import get_model_instance
from causal.main.exceptions import LoggedServiceError
from urlparse import urlparse

DISPLAY_NAME = 'Google Reader'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []
    at = AccessToken.objects.get(service=serv)

    url = at.username
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            item = ServiceItem()
            item.title = entry.title
            # we dont take the summary as its huge
            #if entry.has_key('summary'):
            item.body = ''
            if entry.has_key('links'):
                item.link_back = entry['links']
            if entry.has_key('link'):
                item.link_back = entry['link']
            updated = parser.parse(entry.updated)
            updated = (updated - updated.utcoffset()).replace(tzinfo=None)
            item.created = updated
            item.service = serv
            item.user = user

            # for stats
            o = urlparse(entry.source.link)
            item.source = o.netloc

            item.author = entry.author # person making comment
            # entry.content[0].value == coment
            items.append(item)
    except Exception, e:
        raise LoggedServiceError(original_exception=e)

    return items
