"""Test class for github app."""

from causal.github.service import _convert_feed, _convert_date
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson
import os

try:
    import wingdbstub
except ImportError:
    pass

class TestGithubService(TestCase):
    """Test the module with fixtures."""
    
    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        
        json_file = open(self.path + '/test_data/user_feed.json', 'r')
        json_feed = json_file.read()
        json_file.close()
        
        self.feed = simplejson.loads(json_feed)
        
    def tearDown(self):
        pass

    def test_convert_feed(self):
        """Test processing of raw atom feed."""
        pass
        
    def test_convert_date(self):
        """Test the method for adding the time diff to a date."""
        
        self.assertEqual(_convert_date(self.feed[0]).hour, 22)
        
    def test_convert_date_null_entry(self):
        """Check a None object is handled correctly."""
        
        self.assertFalse(_convert_date(None))

    def test_convert_date_missing_date(self):
        """Check we handle a missing date key"""
        
        tmp_entry = self.feed[0]
        del(tmp_entry['created_at'])
        self.assertFalse(_convert_date(tmp_entry))
        
    def test_convert_broken_feed(self):
        """Test we deal with broken atom feeds."""
        #items = _convert_feed('user', 'github', '')
        #self.assertEqual(0, len(items))
        pass
    
class TestGithubViews(TestCase):
    """Testviews for service."""
    
    fixtures = ['users.json', 'app.json']
    
    def test_auth_view(self):
        """Test /github/auth behaves correctly."""
        
        c = Client()
        c.login(username='bassdread', password='password')
        response = c.post('/github/auth', {'username' : 'username'})
        self.assertEqual('http://testserver/accounts/settings/', response.items()[2][1])
        
    def test_auth_view_get(self):
        """Test /github/auth handles a get request."""
        
        c = Client()
        c.login(username='bassdread', password='password')
        response = c.get('/github/auth')
        self.assertEqual('http://testserver/accounts/settings/', response.items()[2][1])
        
    def test_auth_view_missing_service(self):
        """Test /github/auth handles a get request."""
        
        c = Client()
        c.login(username='admin', password='password')
        response = c.get('/github/auth')
        self.assertEqual('http://testserver/accounts/settings/', response.items()[2][1])       