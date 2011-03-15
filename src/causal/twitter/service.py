"""Does all the fetching from twitter using a oauth token."""
__version__ = '0.1.1'

from causal.main.handlers import BaseServiceHandler
from causal.main.exceptions import LoggedServiceError
from causal.main.models import ServiceItem
from causal.twitter.utils import get_api
from twitter_text import TwitterText
from tweepy import TweepError
import re

DISPLAY_NAME = 'Twitter'
CUSTOM_FORM = False
OAUTH_FORM = True
SETUP_URI = 'causal-twitter-auth'

class ServiceHandler(BaseServiceHandler):
    # We set this as a property so that BaseServiceHandler.enable
    # can forward to the right URI alias
    setup_uri = SETUP_URI

    def get_items(self, since):
        """Use of oauth token to fetch the users updates."""
        api = get_api(self.user_service)

        timeline = []

        # Get the api and bail if we fail
        if api:
            try:
                # Fetch 200 tweets, should be enough for a week...
                timeline = self._convert_feed(
                    api.user_timeline(
                        count=200,
                        include_rts='true'
                    ),
                    since,
                    api.me().screen_name
                )
            except TweepError, exception:
                raise LoggedServiceError(original_exception=exception)

        return timeline

    def _convert_feed(self, feed, since, screen_name):
        """Take the json and convert to ServiceItems"""
        items = []

        for status in feed:
            # We are interested in tweets since
            if status.created_at.date() > since:
                item = ServiceItem()
                item.location = {}
                twitter_text = TwitterText(status.text)
                twitter_text.autolink.auto_link_usernames_or_lists()
                twitter_text.autolink.auto_link_hashtags()
                item.body = unicode(twitter_text.text)

                if re.search("http://yfrog.com/\S*", item.body) \
                   or re.search("http://twitpic.com/\S*", item.body):
                    item.pic_link = True

                item.created = status.created_at
                item.link_back = "http://twitter.com/%s/status/%s" % \
                    (screen_name, str(status.id))
                if status.geo:
                    item.location['lat'] = status.geo['coordinates'][0]
                    item.location['long'] = status.geo['coordinates'][1]
                item.service = self.user_service
                item.user = self.user_service.user
                items.append(item)

        return items

