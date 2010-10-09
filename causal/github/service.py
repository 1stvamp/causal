import time
import feedparser
from datetime import datetime
from BeautifulSoup import Tag, BeautifulSoup as soup
from BeautifulSoup import SoupStrainer
from causal.main.models import AccessToken, ServiceItem
from causal.main.service_utils import get_model_instance

DISPLAY_NAME = 'Github'
CUSTOM_FORM = False
OAUTH_FORM = False

KEEP_TAGS = ('a', 'span', 'code',)

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []
    try:
        at = AccessToken.objects.get(service=serv)

        url = 'https://github.com/%s.atom' % (at.username,)

        feed = feedparser.parse(url)
        links = SoupStrainer('a')
        for entry in feed.entries:
            item = ServiceItem()
            item.title = entry.title
            content = soup(entry.content[0].value)
            for tag in content.findAll(True):
                if tag.name not in KEEP_TAGS:
                    tag.hidden = True
            item.body = content
            # extract the links
            # this is link to github page with everything e.g.:
            # u'http://github.com/bassdread/causal/compare/a76727c436...b1722a6e46'            
            item.link_back = entry['link'] 
            
            # these are the links contained within the body of the entry e.g.:
            # <a href="http://github.com/bassdread/causal/commit/b1722a6e46b77941f75d34d46125522ed535e842">b1722a6</a>
            parsed_links = [tag for tag in soup(str(content), parseOnlyThese=links)]
            if parsed_links:
                item.links = []
                for link in parsed_links:
                    item.links.append(str(link).split('"')[1])
            item.created = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            item.service = serv
            items.append(item)
    except:
        return False

    return items
