"""Test suite for delicious services."""

from bunch import Bunch
from causal.facebook.service import _convert_feed
from django.utils import simplejson
from django.test import TestCase
import os

try:
    import wingdbstub
except ImportError:
    pass

class TestFacebookService(TestCase):
    """Test the module with fixtures."""

    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        
    def tearDown(self):
        pass

    def _convert_status_feed(self):
        """Test we can convert statuses from facebook."""
         
        test_statuses = []
        
        for i in range(0,5):
            b = Bunch(message='Syn %s' %(str(i)), status_id=i, time=1296544805, uid=i)
            test_statuses.append(b)
            