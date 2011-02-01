import httplib2
import oauth2 as oauth
from datetime import datetime
from causal.main.models import ServiceItem, AccessToken
from causal.main.service_utils import get_model_instance
from facegraph.fql import FQL
from causal.main.exceptions import LoggedServiceError
from django.shortcuts import render_to_response, redirect
from datetime import datetime, timedelta
import time

DISPLAY_NAME = 'Facebook'
CUSTOM_FORM = False
OAUTH_FORM = True

STATUS_FQL = """SELECT uid,status_id,message,time FROM status WHERE uid = me() AND time > %s"""
#TAGGED_FQL = """SELECT post_id,actor_id FROM stream_tag WHERE target_id=me()""" # currently unable to spec time
LINKED_FQL = """SELECT owner_comment,created_time,title,summary,url 
FROM link WHERE owner=me() AND created_time > %s"""

STREAM_FQL = """SELECT likes,message,created_time,comments,permalink,privacy,source_id
FROM stream WHERE filter_key IN 
(SELECT filter_key FROM stream_filter WHERE uid = me()) AND created_time > %s"""

USER_NAME_FETCH = """SELECT name, pic_small FROM user WHERE uid=%s"""

def enable():
    """Setup and authorise the service."""
    return redirect('causal-facebook-auth')

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)

    try:
        q = FQL(at.oauth_token)
        week_ago_epoch = time.mktime(since.timetuple())
        status_stream = q(STATUS_FQL % int(week_ago_epoch))
            
    except Exception, e:
        raise LoggedServiceError(original_exception=e)

    if getattr(status_stream, 'error_code', False):
        raise LoggedServiceError(
        'Facebook service failed to fetch items for causal-user %s, error: %s' % \
            (user.username, results['error_msg'])
        )
    return _convert_status_feed(serv, user, status_stream, since)

def _convert_status_feed(serv, user, user_stream, since):
    """Take the feed of status updates from facebook and convert it to 
    ServiceItems."""

    items = []
    
    for entry in user_stream:
        if entry.has_key('message'):
            item = ServiceItem()
            item.created = datetime.fromtimestamp(entry['time'])
            item.title = entry['message']
            item.link_back = \
                "http://www.facebook.com/chris.hannam/posts/%s?notif_t=feed_comment" % (entry['status_id'])
            item.service = serv
            item.user = user
            items.append(item)

    return items