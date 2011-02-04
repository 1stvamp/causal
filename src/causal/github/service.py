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
    serv = model_instance or get_model_instance(user, __name__)
    items = []
    at = AccessToken.objects.get(service=serv)

    user_feed = get_data(
                serv,
                'http://github.com/%s.json' % (serv.user.username),
                disable_oauth=True)

    return _convert_feed(serv.user.username, serv, user_feed, since)

def _convert_feed(user, serv, feed, since):
    """Take the user's atom feed."""

    items = []

    for entry in feed:
        if entry['public']:
            date, time, offset = entry['created_at'].rsplit(' ')
            created = datetime.strptime(date + ' ' + time, '%Y/%m/%d %H:%M:%S')
            if created.date() > since:
                item = ServiceItem()
                item.title = "%s for %s" % (entry['type'], entry['payload']['repo'])

                item.body = ''
                for commit in entry['payload']['shas']:
                    item.body = item.body + commit[2] + ' '
                item.created = created
                item.link_back = entry['url']
                item.service = serv
                item.user = user
                items.append(item)

    return items

def get_stats_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []
    at = AccessToken.objects.get(service=serv)

    user_feed = get_data(
                serv,
                'http://github.com/%s.json' % (serv.user.username),
                disable_oauth=True)

    return _convert_stats_feed(serv.user.username, serv, user_feed, since)

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

            offset = offset[1:]
            offset = offset[:2]
            time_offset = timedelta(hours=int(offset))

            created = datetime.strptime(date + ' ' + time, '%Y/%m/%d %H:%M:%S') + time_offset
            if created.date() > since:
                hour = created.strftime('%H')
                if commit_times.has_key(hour+' ish'):
                    commit_times[hour+' ish'] = commit_times[hour+' ish'] + 1
                else:
                    commit_times[hour+' ish'] = 1

                item = ServiceItem()
                item.title = "%s for %s" % (entry['type'], entry['payload']['repo'])
                item.body = ''
                for commit in entry['payload']['shas']:
                    item.body = item.body + commit[2] + ' '
                item.created = created
                item.link_back = entry['url']
                item.service = serv
                item.user = user
                items.append(item)

    commit_times = SortedDict(sorted(commit_times.items(),
                                    reverse=True, key=lambda x: x[1]))

    return items, avatar, commit_times
