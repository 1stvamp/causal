"""Test class for github app."""

from causal.github.service import _convert_feed
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
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
        
        items = _convert_feed(atom_feed)
        pass