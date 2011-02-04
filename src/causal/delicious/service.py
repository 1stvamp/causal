from causal.main.models import ServiceItem
from causal.main.utils.services import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError
from django.shortcuts import render_to_response, redirect
from causal.main.models import AccessToken, ServiceItem
from dateutil import parser
from datetime import datetime, timedelta
from django.utils import simplejson

DISPLAY_NAME = 'Delicious'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)

    at = AccessToken.objects.get(service=serv)
    url = 'http://feeds.delicious.com/v2/json/%s?count=100' % (at.username,)

    user_feed = get_data(
        serv,
        url,
        disable_oauth=True
        )

    return _convert_feed(serv, user, user_feed, since)

def _convert_feed(serv, user, json, since):
    """Convert the json feed into Service Items limiting on since"""

    items = []

    # FIXME add filter on date!
    for entry in json:
        # check we have a valid feed
        if entry != '404 Not Found':
            item = ServiceItem()
            created = datetime.strptime(entry['dt'], '%Y-%m-%dT%H:%M:%SZ') #'2010-11-23T22:03:29Z'
            if created.date() >= since:
                try:
                    item.title = entry['d']
                    item.body = entry['n']
                    item.created = created
                    item.link_back = entry['u']
                    item.notes = entry['n']
                    item.tags = entry['t']
                    item.service = serv
                    item.user = user
                    items.append(item)
                except:
                    pass

    return items
