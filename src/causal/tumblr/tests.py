from django.test import TestCase
from causal.delicious.service import _convert_feed

try:
    import wingdbstub
except ImportError:
    pass

class TestTumblrService(TestCase):
    """Test the module with fixtures."""

    def setUp(self):
        f = open(__file__.rpartition('/')[0] + '/test_data/test_data.xml', 'r')
        self.json_feed = f.read()
        f.close()
        
    def tearDown(self):
        pass

    def test_convert_feed(self):
        """Check we get back a correctly formed list of ServiceItems"""
        pass