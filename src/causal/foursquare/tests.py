"""Test class for Four Square app."""

from causal.foursquare.views import auth
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

try:
    import wingdbstub
except ImportError:
    pass

class TestFourSquareViews(TestCase):
    """Test the module with fixtures."""
    
    fixtures = ['auth_data.json']

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('user', 'user@example.com', 'password')
        user.save()
        
    def tearDown(self):
        pass

    def test_auth(self):
        """Test /foursquare/auth does the right thing."""
        #reverse('arch-summary', args=[1945])
        #self.client.get('/foursquare/auth')
        res = self.client.post('/accounts/login/', {'username': 'user', 'password': 'password'})
        self.client.get(reverse('causal-foursquare-auth'))
        pass
        