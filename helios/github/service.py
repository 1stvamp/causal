import time
import feedparser
from BeautifulSoup import Tag, BeautifulSoup as soup
from datetime import datetime
from django.utils import simplejson
from django.utils.safestring import mark_safe
from helios.main.models import AccessToken, UserService, ServiceItem

display_name = 'Github'

KEEP_TAGS = ('a', 'span', 'code',)

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user)
    items = []
    try:
        at = AccessToken.objects.get(service=serv)

        url = 'https://github.com/%s.private.actor.atom?token=%s' % (at.username, at.api_token,)

        feed = feedparser.parse(url)

        for entry in feed.entries:
            item = ServiceItem()
            item.title = entry.title
            content = soup(entry.content[0].value)
            for tag in content.findAll(True):
                if tag.name not in KEEP_TAGS:
                    tag.hidden = True
            item.body = mark_safe(content)
            item.created = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            item.service = serv
            items.append(item)
    except Exception, e:
        print e
        return False

    return items

def get_model_instance(user):
    return UserService.objects.get(user=user, app__module_name=__package__)