import httplib2
import oauth2 as oauth
from datetime import datetime, timedelta
from causal.main.models import ServiceItem
from causal.main.service_utils import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError
from django.shortcuts import render_to_response, redirect

DISPLAY_NAME = 'Foursquare'
CUSTOM_FORM = False
OAUTH_FORM = True

def enable():
    """Setup and authorise the service."""
    return redirect('causal-foursquare-auth')

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    try:
        checkins = get_data(serv, 'http://api.foursquare.com/v1/history.json')
    except Exception, e:
        raise LoggedServiceError(original_exception=e)

    if checkins and checkins.has_key('checkins'):
        for checkin in checkins['checkins']:
            item = ServiceItem()
            item.location = {}
            item.link_back = 'http://foursquare.com/venue/%s' % checkin['venue']['id']
            item.title = checkin['venue']['name']
            if checkin.has_key('shout') and checkin['shout']:
                item.body = checkin['shout']
            else:
                item.body = checkin['venue']['city']
            if checkin['venue'].has_key('geolat') and checkin['venue']['geolat']:
                item.location['lat'] = checkin['venue']['geolat']
                item.location['long'] = checkin['venue']['geolong']
            item.created = datetime.strptime(checkin['created'].replace(' +0000', ''), '%a, %d %b %y %H:%M:%S')
            item.service = serv
            if checkin['venue'].has_key('primarycategory'):
                item.icon = checkin['venue']['primarycategory']['iconurl']
            item.user = user
            items.append(item)
            del(item)
    return items
