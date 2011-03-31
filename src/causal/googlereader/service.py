import time
import feedparser
from dateutil import parser
from datetime import datetime
from causal.main.handlers import BaseServiceHandler
from causal.main.models import ServiceItem
from causal.main.exceptions import LoggedServiceError
from urlparse import urlparse


class ServiceHandler(BaseServiceHandler):
    display_name = 'Google Reader'

    def get_items(self, since):
        items = []

        try:
            feed = feedparser.parse(
                'http://www.google.com/reader/public/atom/user/%s/state/com.google/broadcast' % (
                    self.service.auth.secret,
                )
            )
            for entry in feed.entries:
                updated = parser.parse(entry.updated)
                updated = (updated - updated.utcoffset()).replace(tzinfo=None)
                if updated.date() >= since:
                    item = ServiceItem()
                    item.title = entry.title
                    # We dont take the summary as its huge
                    item.body = ''
                    if entry.has_key('links'):
                        item.link_back = entry['links']
                    if entry.has_key('link'):
                        item.link_back = entry['link']

                    item.created = updated
                    item.service = self.service

                    # For stats
                    o = urlparse(entry.source.link)
                    item.source = o.netloc

                    # Person making comment
                    item.author = entry.author
                    items.append(item)
        except Exception, e:
            raise LoggedServiceError(original_exception=e)

        return items
