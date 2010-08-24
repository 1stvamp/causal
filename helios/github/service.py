import time
import feedparser
from BeautifulSoup import Tag, BeautifulSoup as soup
from datetime import datetime
from helios.main.models import AccessToken, ServiceItem
from helios.main.service_utils import get_model_instance

DISPLAY_NAME = 'Github'

KEEP_TAGS = ('a', 'span', 'code',)

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
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
            item.body = content
            item.created = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            item.service = serv
            items.append(item)
    except:
        return False

    return items
