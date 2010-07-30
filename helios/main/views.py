from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta, date
from models import OAuthAccessToken, OAuthRequestToken, LastFMSettings
from forms import RegistrationForm, LastFMSettingsForm
import oauth2 as oauth
from settings import OAUTH_APP_SETTINGS
from django.utils import simplejson
import httplib2
import flickrapi

def get_access_token(service, user):
    """Get token if it exists for the service specified."""

    access_token = None

    params = {
        'user' : user,
        'service' : service,
    }

    access_token_list = OAuthAccessToken.objects.filter(**params)

    if access_token_list:
        access_token = access_token_list[0]

    return access_token

@login_required(redirect_field_name='redirect_to')
def history(request):

    template_values = {}

    if request.method == 'GET':


        days = []
        day_one = date.today() - timedelta(days=7)

        for i in range(0,7):
            dt = date.today()
            d = timedelta(days=i)
            lasttime = dt-d
            days.append({lasttime.strftime('%A') : []})

        # final averaged list
        geo_locations = []

        access_token = get_access_token('twitter', request.user)

        if access_token:

            consumer = oauth.Consumer(OAUTH_APP_SETTINGS['twitter']['consumer_key'],
                                      OAUTH_APP_SETTINGS['twitter']['consumer_secret'])
            token = oauth.Token(access_token.oauth_token , access_token.oauth_token_secret)

            client = oauth.Client(consumer, token)
            url = OAUTH_APP_SETTINGS['twitter']['default_api_prefix'] + '/statuses/user_timeline' + OAUTH_APP_SETTINGS['twitter']['default_api_suffix'] + '?count=70'
            resp, content = client.request(url, "GET")

            tweets = simplejson.loads(content)
            for tweet in tweets:
                hour = timedelta(hours=1)
                tweet['created_at'] = tweet['created_at'].replace(' +0000','')
                record = {
                    'date' : datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %Y') + hour,
                    'info' : tweet['text'],
                    'class' : 'twitter'
                }
                if tweet['geo']:
                    record['coordinates'] = {'lat' : tweet['geo']['coordinates'][0], 'long' : tweet['geo']['coordinates'][1]}
                    
                days = in_date_range(days, record, day_one)

        access_token = get_access_token('foursquare', request.user)

        if access_token:
            consumer = oauth.Consumer(OAUTH_APP_SETTINGS['foursquare']['consumer_key'],
                                      OAUTH_APP_SETTINGS['foursquare']['consumer_secret'])
            token = oauth.Token(access_token.oauth_token , access_token.oauth_token_secret)

            client = oauth.Client(consumer, token)
            url = OAUTH_APP_SETTINGS['foursquare']['default_api_prefix'] + '/v1/history'+ OAUTH_APP_SETTINGS['foursquare']['default_api_suffix']
            resp, content = client.request(url, "GET")
            checkins = simplejson.loads(content)
            for checkin in checkins['checkins']:
                hour = timedelta(hours=1)
                checkin['created'] = checkin['created'].replace(' +0000', '')
                record = {
                    'date' : datetime.strptime(checkin['created'], '%a, %d %b %y %H:%M:%S')+ hour,
                    'info' : checkin['venue']['name'],
                    'class' : 'foursquare',
                }
                days = in_date_range(days, record, day_one)
                
        if request.user.lastfmsettings_set.count() > 0:
            fm = request.user.lastfmsettings_set.get()
            if fm:
                url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=09f1c061fc65a7bc08fb3ad95222d16e&format=json' % fm.username
                h = httplib2.Http()
                resp, content = h.request(url, "GET")
                tracks_listing = simplejson.loads(content)
                hour = timedelta(hours=1)
                for track in tracks_listing['recenttracks']['track']:
                    if track.has_key('date'):
                        record = {'info' : track['artist']['#text'] + ' ' + track['name'],
                             'date' : datetime.strptime(track['date']['#text'], '%d %b %Y, %H:%M') + hour,
                             'class': 'lastfm'}
                        days = in_date_range(days, record, day_one)

        url = 'http://github.com/api/v2/json/repos/show/bassdread'
        h = httplib2.Http()
        resp, content = h.request(url, "GET")

        git_hub = simplejson.loads(content)
        repos = []
        
        for repo in git_hub['repositories']:


            url = 'http://github.com/api/v2/json/commits/list/bassdread/%s/master' % repo['name']
            resp, content = h.request(url, "GET")
            commits = simplejson.loads(content)

            for commit in commits['commits']:
                commited_datetime = commit['committed_date']
                utc_offset = commited_datetime.rsplit('-', 1)[1]
                utc_offset = utc_offset[:2]
                utc_offset_delta = timedelta(hours=int(utc_offset) + 1)

                commited_datetime = datetime.strptime(commited_datetime.rsplit('-', 1)[0], '%Y-%m-%dT%H:%M:%S')
                commited_datetime = commited_datetime + utc_offset_delta
                record = { 
                    'info' : 'Project: ' + repo['name'],
                    'date' : commited_datetime,
                    'class' : 'github',
                    'message' : commit['message'],
                }

                days = in_date_range(days, record, day_one)

        # flickr
        #44f769edefafed6115fe0ceead554816
        #07b50c863cd8871e
        
        flickr = flickrapi.FlickrAPI('44f769edefafed6115fe0ceead554816')
        
        photos_json = flickr.photos_search(user_id='50685137@N00', per_page='10', format='json')
        photos_json = photos_json.replace('jsonFlickrApi(', '')
        photos_json = photos_json.rstrip(')')
        photos = simplejson.loads(photos_json)
        
        for photo in photos['photos']['photo']:
            # flickr.photos.getInfo
            pic = flickr.photos_getInfo(photo_id=photo['id'], format='json')
            pic = pic.replace('jsonFlickrApi(', '')
            pic = pic.rstrip(')')
            p = simplejson.loads(pic)
            epoch = p['photo']['dateuploaded']
            
            record = { 
                    'info' : p['photo']['title']['_content'] + ' : ' + p['photo']['urls']['url'][0]['_content'],
                    'date' : datetime.fromtimestamp(float(epoch)),
                    'class' : 'flickr',
                }
            
            days = in_date_range(days, record, day_one)
                    
        if days:
            for day in days:
                day[day.keys()[0]].sort(key=lambda item:item['date'], reverse=True)
            template_values['days'] = days

    return render_to_response('index.html',template_values,
                              context_instance=RequestContext(request))

def in_date_range(days, record, day_one):
    """Check if an entry is in our week date range"""
    for day in days:
        if day.keys()[0] == record['date'].strftime('%A')\
           and record['date'].date() > day_one:
            day[day.keys()[0]].append(record)
    return days

@login_required(redirect_field_name='redirect_to')
def oauth_login(request, service=None):

    if request.method == 'GET':
        oauth_details = OAUTH_APP_SETTINGS[service]
        consumer = oauth.Consumer(OAUTH_APP_SETTINGS[service]['consumer_key'],
                                  OAUTH_APP_SETTINGS[service]['consumer_secret'])

        client = oauth.Client(consumer)
        resp, content = client.request(oauth_details['request_token_url'], "GET")

        if resp['status'] != '200':
            print "fail"

        request_token_params = dict((token.split('=') for token in content.split('&')))

        token = OAuthRequestToken()
        token.service=service
        token.user = request.user
        token.oauth_token = request_token_params['oauth_token']
        token.oauth_token_secret = request_token_params['oauth_token_secret']
        token.created = datetime.now()
        token.save()

    return HttpResponseRedirect("%s?oauth_token=%s" % (oauth_details['user_auth_url'],
                                                       request_token_params['oauth_token']))

def oauth_callback(request, service=None):
    consumer = oauth.Consumer(OAUTH_APP_SETTINGS[service]['consumer_key'],
                              OAUTH_APP_SETTINGS[service]['consumer_secret'])

    params = {
        'oauth_token' : request.GET['oauth_token'],
        'service' : service,
    }

    request_token = OAuthRequestToken.objects.filter(**params)[0]

    token = oauth.Token(request_token.oauth_token, request_token.oauth_token_secret)
    client = oauth.Client(consumer, token)
    resp, content = client.request(OAUTH_APP_SETTINGS[service]['access_token_url'], "POST")

    access_token = dict((token.split('=') for token in content.split('&')))

    token_save = OAuthAccessToken()
    token_save.service=service
    token_save.user=request.user
    token_save.create=datetime.now()
    token_save.oauth_token=access_token['oauth_token']
    token_save.oauth_token_secret=access_token['oauth_token_secret']

    token_save.save()

    return HttpResponseRedirect('/history/')

def register(request):
    form = RegistrationForm()

    if request.user.is_authenticated():
        return HttpResponseRedirect('/history/')

    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(form.cleaned_data['email'],
                                     form.cleaned_data['email'],
                                     form.cleaned_data['password1'])

            user = authenticate(username=form.cleaned_data['email'],
                                password=form.cleaned_data['password1'])
            login(request, user)

            return HttpResponseRedirect('/history/')

    return render_to_response('accounts/register.html',{
        'form' : form,
        },
                              context_instance=RequestContext(request))

@login_required(redirect_field_name='redirect_to')
def profile(request):
    form = LastFMSettingsForm()
    twitter = None
    foursquare = None
    lastfm = None

    if request.POST:
        form = LastFMSettingsForm(request.POST)
        if form.is_valid():
            last = LastFMSettings()
            last.user = request.user
            last.username = form.cleaned_data['username']
            last.save()

    tokens = request.user.oauthaccesstoken_set.all()
    for token in tokens:
        if token.service == 'twitter':
            twitter = True
        if token.service == 'foursquare':
            foursquare = True

    return render_to_response('accounts/profile.html',{
        'form' : form,
        'twitter' : twitter,
        'foursquare' : foursquare,
        },
                              context_instance=RequestContext(request))
