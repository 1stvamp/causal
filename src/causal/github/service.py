import time
import feedparser
from dateutil import parser
from datetime import datetime, timedelta
from BeautifulSoup import Tag, BeautifulSoup as soup
from BeautifulSoup import SoupStrainer
from causal.main.models import AccessToken, ServiceItem
from causal.main.utils.services import get_model_instance, get_data
from causal.main.exceptions import LoggedServiceError
from django.utils.datastructures import SortedDict

DISPLAY_NAME = 'Github'
CUSTOM_FORM = False
OAUTH_FORM = False

KEEP_TAGS = ('a', 'span', 'code',)

def get_items(user, since, model_instance=None):
    """Fetch updates."""

    serv = model_instance or get_model_instance(user, __name__)

    at = AccessToken.objects.get(service=serv)
    return _convert_feed(at.username, 
                         serv, 
                         _get_feed(user, serv), 
                         since)


def get_stats_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []
    at = AccessToken.objects.get(service=serv)

    user_feed = get_data(
                serv,
                'http://github.com/%s.json' % (at.username),
                disable_oauth=True)

    return _convert_stats_feed(at.username, serv, user_feed, since)

def _get_feed(user, serv):
    """Fetch the raw feed from github."""

    user_feed = get_data(
            serv,
            'http://github.com/%s.json' % (user),
            disable_oauth=True)
    
    return user_feed

def _convert_feed(user, serv, feed, since):
    """Take the user's atom feed."""

    items = []

    for entry in feed:
        if entry['public']:
            created = _convert_date(entry)
            
            if created.date() > since:
                item = ServiceItem()
                _set_title_body(entry, item)
                item.created = created
                item.link_back = entry['url']
                item.service = serv
                item.user = user
                items.append(item)

    return items

def _convert_date(entry):
    """Apply the offset from githuub timing to the date."""

    converted_date = None
    
    if entry and entry.has_key('created_at'):
    
        date, time, offset = entry['created_at'].rsplit(' ')

        offset = offset[1:]
        offset = offset[:2]
        time_offset = timedelta(hours=int(offset))

        converted_date = datetime.strptime(date + ' ' + time, '%Y/%m/%d %H:%M:%S') + time_offset
        
    return converted_date

def _convert_stats_feed(user, serv, feed, since):
    """Take the user's atom feed."""

    items = []
    avatar = ""

    if feed[0]['actor_attributes'].has_key('gravatar_id'):
        avatar = 'http://www.gravatar.com/avatar/%s' % feed[0]['actor_attributes']['gravatar_id']

    commit_times = {}

    for entry in feed:
        if entry['public']:
            date, time, offset = entry['created_at'].rsplit(' ')
            created = _convert_date(entry)
            
            if created.date() > since:
                hour = created.strftime('%H')
                if commit_times.has_key(hour + ' ish'):
                    commit_times[hour+' ish'] = commit_times[hour+' ish'] + 1
                else:
                    commit_times[hour+' ish'] = 1

                item = ServiceItem()
                _set_title_body(entry, item)
                item.created = created
                item.link_back = entry['url']
                item.service = serv
                item.user = user
                items.append(item)

    commit_times = SortedDict(sorted(commit_times.items(),
                                    reverse=True, key=lambda x: x[1]))

    return items, avatar, commit_times

def _set_title_body(entry, item):
    """Set the title and body based on the event type."""
    
    if entry['type'] == 'CreateEvent':
        item.title = "Created branch %s from %s" % (entry['payload']['object_name'],entry['payload']['name'])
    else:
        item.title = "%s for %s" % (entry['type'], entry['payload']['repo'])
    item.body = ''
    
    if entry['type'] == 'IssuesEvent':
        item.body = "Issue #%s was %s." % (str(entry['payload']['number']), entry['payload']['action'])
    elif entry['type'] == 'ForkEvent':
        item.body = "Repo %s forked." % (entry['payload']['repo'])
    elif entry['type'] == 'PushEvent':
        item.body = "Pushed to repo %s with comment %s." % (entry['payload']['repo'], entry['payload']['shas'][0][2])
    elif entry['type'] == 'CreateEvent':
        item.body = "Branch %s for %s." % (entry['payload']['object_name'], entry['payload']['name'])
    elif entry['type'] == 'WatchEvent':
        item.body = "Started watching %s." % (entry['payload']['repo'])
    elif entry['type'] == 'FollowEvent':
        item.body = "Started following %s." % (entry['payload']['target']['login'])
    elif entry['type'] == 'GollumEvent':
        pass