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

    def test_history_view(self):
        """Test raw history view from main."""

        post_params = {}

        response = self.client.post(reverse('history'), post_params)
        # Test we get redirected to login screen
        self.assertEquals(response.status_code, 302)

    def _login(self):
        """Log a user in."""
        self.client = Client()
        self.client.post(
                '/login/',
                {
                    'username': self.user_details['username'],
                    'password': self.user_detauls['password'],
                }
        )

    def test_add_image_html(self):
        """Test replacing twitpic text with a link to twit pic."""
        tweet = "Some text #ahashtag http://twitpic.com/354bkr some more text."
        converted_tweet = 'Some text #ahashtag http://twitpic.com/354bkr some more text. <img src="http://twitpic.com/show/mini/354bkr"/>'
        self.assertTrue(_add_image_html(tweet), converted_tweet)
        