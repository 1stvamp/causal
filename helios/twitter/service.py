__version__ = '0.1.1'

from django.shortcuts import render_to_response, redirect
from helios.main.models import UserService, ServiceItem
from helios.twitter.utils import get_api, user_login, get_model_instance

display_name = 'Twitter'

def get_items(user, since, model_instance=None):
    items = []
    serv = model_instance or get_model_instance(user)

    api = get_api(serv)
    if not api:
        return False

    timeline = api.search(
        "from:%s" % (api.me.screen_name),
        since=since.strftime("%Y-%m-%d"),
        rpp=100
    )
    for status in timeline:
        item = ServiceItem()
        item.body = status.text
        item.created =status.created_at
        if status.geo:
            item.location['lat'] = status.geo[0]
            item.location['long'] = status.geo[1]
        item.service = serv

