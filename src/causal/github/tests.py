"""Test class for github app."""

from causal.github.service import _convert_feed
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
import feedparser
import os

try:
    import wingdbstub
except ImportError:
    pass

class TestGithubViews(TestCase):
    """Test the module with fixtures."""

    def setUp(self):
        #self.client = Client()
        #user = User.objects.create_user('user', 'user@example.com', 'password')
        #user.save()
        self.path = os.path.dirname(os.path.realpath(__file__))
        
    def tearDown(self):
        pass

    def test_convert_feed(self):
        """Test processing of raw atom feed."""
        atom_file = open(self.path + '/test_data/user.atom', 'r')
        atom_feed = atom_file.read()
        atom_file.close()
        atom_feed = feedparser.parse(atom_feed)
        items = _convert_feed('user', 'github', atom_feed)
        self.assertEqual(35, len(items))
        
    def test_convert_broken_feed(self):
        """Test we deal with broken atom feeds."""
        items = _convert_feed('user', 'github', '')
        self.assertEqual(0, len(items))
       