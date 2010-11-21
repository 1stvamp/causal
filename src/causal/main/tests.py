from django.test import TestCase
from causal.main.models import User, OAuthSetting
from causal.main.views import history
from django.test.client import Client
from django.core.urlresolvers import reverse
from views import _add_image_html

try:
    import wingdbstub
except ImportError:
    pass

class TestMain(TestCase):
    """Test the module with fixtures."""

    fixtures = ['oauth_settings.json']
    user_details = {
        'username': 'test_user',
        'email': 'test_user@example.com',
        'password': 'password',
    }

    def setUp(self):
        """Make sure we have a user and any other bits and bots for tests"""
        self.user = User.objects.create_user(**self.user_details)
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_add_image_html_twitpic(self):
        """Test replacing twitpic text with a link to twitpic."""
        tweet = "Some text #ahashtag http://twitpic.com/354bkr some more text."
        converted_tweet = 'Some text #ahashtag http://twitpic.com/354bkr some more text. </br> <a href="http://twitpic.com/354bkr"><img src="http://twitpic.com/show/mini/354bkr"/></a>'
        self.assertEqual(_add_image_html(tweet), converted_tweet)
        
    def test_add_image_html_yfrogpic(self):
        """Test replacing yfrog pic text with a link to yfrog pic."""
        tweet = "Some text #ahashtag http://yfrog.com/b9hmwkj some more text."
        converted_tweet = 'Some text #ahashtag http://yfrog.com/b9hmwkj some more text. </br> <a href="http://yfrog.com/b9hmwkj"><img src="http://yfrog.com/b9hmwkj.th.jpg"/></a>'
        self.assertEqual(_add_image_html(tweet), converted_tweet)
        