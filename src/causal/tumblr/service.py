from causal.main.models import ServiceItem
from causal.main.service_utils import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError
from django.shortcuts import render_to_response, redirect
from causal.main.models import AccessToken, ServiceItem
from causal.main.exceptions import LoggedServiceError
from dateutil import parser
from datetime import datetime, timedelta
from lxml import etree
import feedparser
import httplib2

DISPLAY_NAME = 'Tumblr'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    
    at = AccessToken.objects.get(service=serv)
    url = 'http://%s.tumblr.com/api/read' % (at.username,)
    h = httplib2.Http()
    resp, content = h.request(url, "GET")
    
    return _convert_feed(content, serv, user)
    
def _convert_feed(feed, serv, user):
    items = []
    try:
        tree = etree.fromstring(feed)
        
        for entry in tree.xpath('/tumblr/posts/post'):
            item = ServiceItem()
            if entry.xpath('regular-title') and entry.xpath('regular-body'):
                item.title = entry.xpath('regular-title')[0].text
                item.body = entry.xpath('regular-body')[0].text
                updated = parser.parse(entry.attrib['date-gmt'])
                updated = (updated - updated.utcoffset()).replace(tzinfo=None)
                item.created = updated
                item.link_back = entry.attrib['url']
                item.service = serv
                item.user = user
                items.append(item)
    except Exception, e:
        raise LoggedServiceError(original_exception=e)
        
    return items
