import oauth2 as oauth
from datetime import datetime, timedelta
from causal.main.models import ServiceItem, AccessToken
from causal.main.service_utils import get_model_instance, get_data

DISPLAY_NAME = 'Last.fm'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)

    tracks_listing = get_data(
        serv,
        'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json' \
            % (at.username, at.api_token,),
        disable_oauth=True
    )
    for track in tracks_listing['recenttracks']['track']:
        if track.has_key('date'):
            item = ServiceItem()
            item.title = track['name']
            item.body = 'by %s' % (track['artist']['#text'],)
            item.created = datetime.strptime(track['date']['#text'], '%d %b %Y, %H:%M') \
                + timedelta(hours=datetime.now().utcoffset() or 0),
            item.service = serv
            items.append(item)

            if type(item.created) == tuple and len(item.created):
                item.created = item.created[0]

    #fav_artists = get_data(
        #serv,
        #'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&period=7day&format=json' \
            #% (at.username, at.api_token,),
        #disable_oauth=True
    #)
    #for artist in fav_artists['topartists']['artist']:
        #artist_save = {
            #'name' : artist['name'],
            #'rank' : artist['@attr']['rank'],
            #'plays' : artist['playcount'],
            #'image' : artist['image'][2]['#text'],
        #}
        ## fetch up coming gigs
        #url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getevents&artist=%s&api_key=09f1c061fc65a7bc08fb3ad95222d16e&format=json' % artist['name'].replace(' ', '+')
        #h = httplib2.Http()
        #resp, content = h.request(url, "GET")
        #events = simplejson.loads(content)
        #if events['events'].has_key('event'):
            #artist_save['venue_name'] = events['events']['event'][0]['venue']['name']
            #artist_save['date'] = events['events']['event'][0]['startDate']

        #template_values['lastfm_artists'].append(artist_save)

    return items
