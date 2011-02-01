"""Test class for Flickr app."""

from causal.flickr.views import auth
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

try:
    import wingdbstub
except ImportError:
    pass

class TestFlickrViews(TestCase):
    """Test the module with fixtures."""
    
    fixtures = ['auth_data.json']

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('user', 'user@example.com', 'password')
        user.save()
        
    def tearDown(self):
        pass

    def test_auth(self):
        """Test /flickr/auth does the right thing."""
        pass
        