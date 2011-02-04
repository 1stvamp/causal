from causal.main.models import ServiceItem
from causal.main.utils.services import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError
from django.shortcuts import render_to_response, redirect
from django.utils import simplejson
from causal.main.models import AccessToken, ServiceItem
from causal.main.exceptions import LoggedServiceError
from dateutil import parser
from datetime import datetime, timedelta

import feedparser
import httplib2

DISPLAY_NAME = 'Tumblr'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    
    at = AccessToken.objects.get(service=serv)
    url = 'http://%s.tumblr.com/api/read/json?callback=callback' % (at.username,)
    h = httplib2.Http()
    resp, content = h.request(url, "GET")
    
    return _convert_feed(content, serv, user)
    
def _convert_feed(feed, serv, user):
    items = []
    try:
        feed = feed.replace('callback(', '')
        feed = feed.rstrip(');\n')
        json = simplejson.loads(feed)
        
        for entry in json['posts']:
            item = ServiceItem()
            
            if entry.has_key('regular-title'):
                item.title = entry['regular-title']
            if entry.has_key('regular-body'):
                item.body = entry['regular-body']
            updated = parser.parse(entry['date-gmt'])
            updated = (updated - updated.utcoffset()).replace(tzinfo=None)
            item.created = updated
            item.link_back = entry['url']
            item.service = serv
            item.user = user
            items.append(item)
    except Exception, e:
        raise LoggedServiceError(original_exception=e)
        
    return items
