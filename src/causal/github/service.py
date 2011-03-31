import time
import feedparser
from dateutil import parser
from datetime import datetime, timedelta
from BeautifulSoup import Tag, SoupStrainer, BeautifulSoup as soup
from causal.main.handlers import BaseServiceHandler
from causal.main.models import ServiceItem
from causal.main.utils.services import get_data
from causal.main.exceptions import LoggedServiceError
from django.utils.datastructures import SortedDict

KEEP_TAGS = ('a', 'span', 'code',)

class ServiceHandler(BaseServiceHandler):
    display_name = 'Github'

    def get_items(self, since):
        """Fetch updates.
        """

        return self._convert_feed(
            self._get_feed(),
            since
        )


    def get_stats_items(self, since):
        """Fetch stats updates.
        """

        return self._convert_stats_feed(
            self._get_feed(),
            since
        )

    def _get_feed(self):
        """Fetch the raw feed from github.
        """

        return get_data(
            self.service,
            'http://github.com/%s.json' % (self.service.auth.username,),
            disable_oauth=True
        )

    def _convert_feed(self, feed, since):
        """Take the user's atom feed.
        """

        items = []

        for entry in feed:
            if entry.has_key('public') and entry['public']:
                created = self._convert_date(entry)

                if created.date() > since:
                    item = ServiceItem()
                    self._set_title_body(entry, item)
                    item.created = created
                    if entry['type'] == 'GistEvent':
                        item.link_back = entry['payload']['url']
                    else:
                        if entry.has_key('url'):
                            item.link_back = entry['url']
                    item.service = self.service
                    items.append(item)

        return items

    def _convert_date(self, entry):
        """Apply the offset from githuub timing to the date.
        """

        converted_date = None

        if entry and entry.has_key('created_at'):

            date, time, offset = entry['created_at'].rsplit(' ')

            offset = offset[1:]
            offset = offset[:2]
            time_offset = timedelta(hours=int(offset))

            converted_date = datetime.strptime(date + ' ' + time, '%Y/%m/%d %H:%M:%S') + time_offset

        return converted_date

    def _convert_stats_feed(self, feed, since):
        """Take the user's atom feed.
        """

        items = []
        avatar = ""

        if feed and feed[0]['actor_attributes'].has_key('gravatar_id'):
                avatar = 'http://www.gravatar.com/avatar/%s' % (feed[0]['actor_attributes']['gravatar_id'],)

        commit_times = {}

        for entry in feed:
            if entry['public']:
                date, time, offset = entry['created_at'].rsplit(' ')
                created = self._convert_date(entry)

                if created.date() > since:
                    hour = created.strftime('%H')
                    if commit_times.has_key(hour + ' ish'):
                        commit_times[hour+' ish'] = commit_times[hour+' ish'] + 1
                    else:
                        commit_times[hour+' ish'] = 1

                    item = ServiceItem()
                    self._set_title_body(entry, item)
                    item.created = created
                    if entry.has_key('url'):
                        item.link_back = entry['url']
                    item.service = self.service
                    items.append(item)

        commit_times = SortedDict(sorted(
            commit_times.items(),
            reverse=True,
            key=lambda x: x[1]
        ))

        return items, avatar, commit_times

    def _set_title_body(self, entry, item):
        """Set the title and body based on the event type.
        """

        item.body = ''

        if entry['type'] == 'CreateEvent':
            item.title = "Created branch %s from %s" % (entry['payload']['object_name'],entry['payload']['name'])
        elif entry['type'] == 'GistEvent':
            item.title = "Created gist %s" % (entry['payload']['desc'])
        elif entry['type'] == 'IssuesEvent':
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
        elif entry['type'] == 'GistEvent':
            item.body = "Snippet: %s" % (entry['payload']['snippet'])
        elif entry['type'] == 'DeleteEvent':
            item.body = "Deleted: %s called %s" % (entry['payload']['ref_type'], entry['payload']['ref'])
        elif entry['type'] == 'GollumEvent':
            pass
        else:
            item.title = "Unknown Event!"
