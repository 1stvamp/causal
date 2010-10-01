import httplib2
import oauth2 as oauth
from datetime import datetime, timedelta
from causal.main.models import ServiceItem
from causal.main.service_utils import get_model_instance, get_data

DISPLAY_NAME = 'Foursquare'
CUSTOM_FORM = False
OAUTH_FORM = True

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    checkins = get_data(serv, 'http://api.foursquare.com/v1/history.json')
    if checkins and checkins.has_key('checkins'):
        for checkin in checkins['checkins']:
            item = ServiceItem()
            item.title = "Checked in: %s" % (checkin['venue']['name'],)
            if checkin.has_key('shout') and checkin['shout']:
                item.body = checkin['shout']
            if checkin['venue'].has_key('geolat') and checkin['venue']['geolat']:
                item.location['lat'] = checkin['venue']['geolat']
                item.location['long'] = checkin['venue']['geolong']
            item.created = datetime.strptime(
                checkin['created'].replace(' +0000', ''),
                '%a, %d %b %y %H:%M:%S') + timedelta(hours=datetime.now().utcoffset() or 0)
            item.service = serv
            items.append(item)

    return items
