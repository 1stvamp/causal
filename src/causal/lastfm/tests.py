"""Tests for last.fm app."""

from causal.lastfm.service import _convert_recent_tracks_json
from django.test import TestCase
from django.utils import simplejson

try:
    import wingdbstub
except ImportError:
    pass

class TestLastfmService(TestCase):
    """Test the module with fixtures."""

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_convert_recent_tracks_json(self):
        """Test the method for converting a json feed of recent
        tracks into ServiceItems."""
        json_file = open(__file__.rpartition('/')[0] + '/test_data/recent_tracks.json', 'r')
        recent_tracks = json_file.read()
        json_file.close()
        
        service_items = _convert_recent_tracks_json('username', 'lastfm', simplejson.loads(recent_tracks))
        
        self.assertEqual(len(service_items), 10)
        
    def test_convert_recent_tracks_json_no_recent_tracks(self):
        """Check it deals with no recent tracks."""
        
        json_file = open(__file__.rpartition('/')[0] + '/test_data/no_recent_tracks.json', 'r')
        recent_tracks = json_file.read()
        json_file.close()
        
        service_items = _convert_recent_tracks_json('username', 'lastfm', simplejson.loads(recent_tracks))
        
        self.assertEqual(len(service_items), 0)
        
    def test_convert_recent_tracks_json_unknown_user(self):
        """Check it deals correctly with an unknown username."""
        
        json_file = open(__file__.rpartition('/')[0] + '/test_data/unknown_user.json', 'r')
        recent_tracks = json_file.read()
        json_file.close()
        
        service_items = _convert_recent_tracks_json('username', 'lastfm', simplejson.loads(recent_tracks))
        
        self.assertEqual(len(service_items), 0)