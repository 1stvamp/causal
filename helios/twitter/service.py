__version__ = '0.1.1'

from django.shortcuts import render_to_response, redirect
from helios.main.models import Service, ServiceItem
from helios.twitter.utils import get_api, user_login

display_name = 'Twitter'

def get_items(user, model_instance=None):
    items = []
    serv = model_instance or get_model_instance(user)

    api = get_api(serv)
    if not api:
        r = user_login(serv)
        if r:
            return r
        else:
            return items

    timeline = api.user_timeline(count=50)
    for status in timeline:
        item = ServiceItem()
        item.body = status.text
        item.created =status.created_at
        if status.geo:
            item.location['lat'] = status.geo[0]
            item.location['long'] = status.geo[1]
        item.service = serv

def get_model_instance(user):
    return Service.objects.get(user=user, app_name=__package__)
