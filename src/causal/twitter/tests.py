"""Test class for Twitter app."""

from causal.twitter.service import _convert_feed
from datetime import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson
import os

class TestTwitterService(TestCase):
    """Test the module with fixtures."""
    
    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        
        json_file = open(self.path + '/test_data/user_feed.json', 'r')
        json_feed = json_file.read()
        json_file.close()
        
        self.feed = simplejson.loads(json_feed)
        
        # setup a date 7 days from our test data
        # Fri Feb 11 23:19:40 +0000 2011  '%Y-%m-%dT%H:%M:%S') #'2007-06-26T17:55:03+0000'
        self.since = datetime.strptime("2011-02-11T17:55:03", '%Y-%m-%dT%H:%M:%S').date()
        
    def test_convert_feed(self):
        """Test we get back the correct number of ServiceItems."""
        
        pass