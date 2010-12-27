from django.test import TestCase
from causal.delicious.service import _convert_feed
import feedparser

try:
    import wingdbstub
except ImportError:
    pass

class TestTumblrService(TestCase):
    """Test the module with fixtures."""

    def setUp(self):
        self.rss_feed = """"""
        
    def tearDown(self):
        pass

    def test_convert_feed(self):
        """Check we get back a correctly formed list of ServiceItems"""
        pass