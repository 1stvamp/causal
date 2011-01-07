import oauth2 as oauth
from datetime import datetime, timedelta
from causal.main.models import ServiceItem, AccessToken
from causal.main.service_utils import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError

DISPLAY_NAME = 'Last.fm'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)

    try:
        tracks_listing = get_data(
            serv,
            'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json&limit=200' \
                % (at.username, at.api_token,),
            disable_oauth=True
        )
    except Exception, e:
        raise LoggedServiceError(original_exception=e)

    if tracks_listing.has_key('recenttracks'):
        for track in tracks_listing['recenttracks']['track']:
            if track.has_key('date'):
                item = ServiceItem()
                item.title = track['name']
                item.body = 'by %s' % (track['artist']['#text'],)
                item.link_back = track['url']
                item.created = datetime.strptime(track['date']['#text'], '%d %b %Y, %H:%M')
                item.service = serv
                item.user = user
                items.append(item)
        
                if type(item.created) == tuple and len(item.created):
                    item.created = item.created[0]
    else:
        raise LoggedServiceError(original_exception=e)
    
    return items

def get_artists(user, since, model_instance=None):
    """Get a users top artists."""
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)

    fav_artists = get_data(
        serv,
        'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&period=7day&format=json' \
            % (at.username, at.api_token,),
        disable_oauth=True
    )

    if fav_artists:
        for artist in fav_artists['topartists']['artist']:
            item = ServiceItem()
            item.name = artist['name']
            item.rank = artist['@attr']['rank']
            item.plays = artist['playcount']
            item.image = artist['image'][2]['#text']
            item.artist_url = artist['url']
            items.append(item)

    return items

def get_upcoming_gigs(user, since, model_instance=None, artist=None):
    """Return a list of up coming gigs for the user."""
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)

    gigs = get_data(
        serv,
        'http://ws.audioscrobbler.com/2.0/?method=artist.getevents&artist=%s&api_key=%s&format=json'
            % (artist.replace(' ', '+'), at.api_token,),
        disable_oauth=True
    )

    items = []
    if gigs and gigs.has_key('events') and gigs['events'].has_key('event') :
        for gig in gigs['events']['event']:
            item = ServiceItem()
            item.location = {}
            try:
                if gig.has_key('venue') and gig['venue'].has_key('name') and gig.has_key('startDate'):
                    item.venue_name = gig['venue']['name']
                    item.event_url = gig['url']
                    item.date = gig['startDate']
                    if gig['venue'].has_key('location') and gig['venue']['location'].has_key('geo:point'):
                        item.location['long'] = gig['venue']['location']['geo:point']['geo:long']
                        item.location['lat'] = gig['venue']['location']['geo:point']['geo:lat']
                    items.append(item)
            except:
                pass
    return items
