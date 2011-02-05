"""This module goes and fetches updates from http://last.fm. We
access public json feeds and convert it to our ServiceItem format."""

from causal.main.models import ServiceItem, AccessToken
from causal.main.utils.services import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError
from datetime import datetime
from time import time, mktime

DISPLAY_NAME = 'Last.fm'
CUSTOM_FORM = False
OAUTH_FORM = False
MAX_RESULTS = '200'

def get_items(user, since, model_instance=None):
    """Fetch and filter the updates from Last.fm."""

    serv = model_instance or get_model_instance(user, __name__)
    access_token = AccessToken.objects.get(service=serv)
    tracks_listing = None

    if access_token:
        try:
            t = datetime.now()
            tracks_listing = get_data(
                serv,
                'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json&from=%s&to=%s&limit=%s' \
                    % (access_token.username,
                       access_token.api_token,
                       str(int(mktime(since.timetuple()))),
                       str(int(mktime(t.timetuple()))),
                       MAX_RESULTS),
                disable_oauth=True
            )
        except Exception, exception:
            raise LoggedServiceError(original_exception = exception)

    return _convert_recent_tracks_json(user, serv, tracks_listing)

def _convert_recent_tracks_json(user, serv, json):
    """Convert the json returned from getrecenttrack into ServiceItems."""

    items = []

    if json.has_key('recenttracks') and json['recenttracks'].has_key('track'):
        for track in json['recenttracks']['track']:
            if track.has_key('date'):
                item = ServiceItem()
                item.title = track['name']
                item.body = 'by %s' % (track['artist']['#text'],)
                item.link_back = track['url']
                item.created = datetime.strptime(track['date']['#text'],
                                                 '%d %b %Y, %H:%M')
                item.service = serv
                item.user = user
                items.append(item)

                if type(item.created) == tuple and len(item.created):
                    item.created = item.created[0]

    return items

def get_artists(user, since, model_instance=None):
    """Get a users top artists."""

    serv = model_instance or get_model_instance(user, __name__)
    access_token = AccessToken.objects.get(service=serv)
    fav_artists = None

    if access_token:
        fav_artists = get_data(
            serv,
            'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&period=7day&format=json' \
                % (access_token.username, access_token.api_token,),
            disable_oauth=True
        )

    return _convert_top_artists_json(user, serv, fav_artists)

def _convert_top_artists_json(user, serv, json):
    """Convert json to ServiceItem list."""
    items = []

    if json['topartists'].has_key('artist'):
        for artist in json['topartists']['artist']:
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

    access_token = AccessToken.objects.get(service=serv)

    gigs = get_data(
        serv,
        'http://ws.audioscrobbler.com/2.0/?method=artist.getevents&artist=%s&api_key=%s&format=json'
            % (artist.replace(' ', '+'), access_token.api_token,),
        disable_oauth=True
    )

    items = []

    if gigs and gigs.has_key('events') and gigs['events'].has_key('event') :
        for gig in gigs['events']['event']:
            item = ServiceItem()
            item.location = {}
            try:
                if gig.has_key('venue') and \
                   gig['venue'].has_key('name') and \
                   gig.has_key('startDate'):
                    item.venue_name = gig['venue']['name']
                    item.event_url = gig['url']
                    item.date = gig['startDate']
                    if gig['venue'].has_key('location') and \
                       gig['venue']['location'].has_key('geo:point'):
                        item.location['long'] = \
                            gig['venue']['location']['geo:point']['geo:long']
                        item.location['lat'] = \
                            gig['venue']['location']['geo:point']['geo:lat']
                    items.append(item)
            except:
                pass
    return items
