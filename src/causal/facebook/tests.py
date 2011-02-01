"""Test suite for delicious services."""

from bunch import Bunch
from causal.facebook.service import _convert_status_feed, _convert_link_feed
from datetime import datetime, timedelta, date
from django.utils import simplejson
from django.test import TestCase
import os, time

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
        
        service_items = _convert_status_feed(test_statuses)
 
    def test_convert_link_feed(self):
        """Test converting a feed from Facebook into ServiceItems"""
        
        test_links = []
        
        for i in range(0,5):
            entry = Bunch(created_time = int(time.mktime(datetime.now().timetuple())), 
                      owner_comment = 'http://www.bbc.co.uk/news/12318490%s COMMENT' % (str(i)), 
                      summary = 'This is the summary!', 
                      title = 'Title on the page', 
                      url = 'http://www.bbc.co.uk/news/%s/12318490' % (str(i)))

            test_links.append(entry)
            
        since =  date.today() - timedelta(days=7)
        service_items = _convert_link_feed('facebook', 'username', test_links, since)
        
        self.assertEqual(len(service_items), 5)
            
## links
#>>> a[0]
#Bunch(comments=Bunch(can_post=True, can_remove=False, comment_list=Bunch(), count=0), created_time=1296581334, likes=Bunch(can_like=True, count=1, friends=Bunch(), href='http://www.facebook.com/social_graph.php?node_id=151306858256580&class=LikeManager', sample=[531095458], user_likes=False), message='Quick coffee with the bestie then home to have tea cooked by the boy :) <3', permalink='http://www.facebook.com/katie.v.mitchell/posts/151306858256580', privacy=Bunch(value=''), source_id=830350500)
#>>> a[1]
#Bunch(comments=Bunch(can_post=True, can_remove=False, comment_list=[Bunch(fromid=514021846, id='58013715_181041718601368_2358095', likes=0, text='*Blinks*\n\nUmmmm...\n\n*Blinks twice*\n\nHow about Ibuprofen and Caffeine flavoured?', time=1296581311, user_likes=False), Bunch(fromid=58013715, id='58013715_181041718601368_2358105', likes=0, text='Sleep...', time=1296581442, user_likes=False)], count=8), created_time=1296580369, likes=Bunch(can_like=True, count=0, friends=Bunch(), href='http://www.facebook.com/social_graph.php?node_id=181041718601368&class=LikeManager', sample=Bunch(), user_likes=False), message='has a poorly elbow, a poorly head, and a poorly will to stay awake...', permalink='http://www.facebook.com/laura.kishimoto/posts/181041718601368', privacy=Bunch(value=''), source_id=58013715)
#>>> 