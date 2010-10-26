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

def get_items(user, since, model_instance=None, stats=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)

    try:
        q = FQL(at.oauth_token)
        week_ago = datetime.now() - timedelta(days=7)
        week_ago_epoch = time.mktime(week_ago.timetuple())
        status = q(STATUS_FQL % int(week_ago_epoch))
        if stats:
            links = q(LINKED_FQL % int(week_ago_epoch))
            stream = q(STREAM_FQL % int(week_ago_epoch))
    except Exception, e:
        raise LoggedServiceError(original_exception=e)

    if getattr(status, 'error_code', False):
        raise LoggedServiceError(
        'Facebook service failed to fetch items for causal-user %s, error: %s' % \
            (user.username, results['error_msg'])
        )
    else:
        for stat in status:
            if stat.has_key('message'):
                item = ServiceItem()
                item.created = datetime.fromtimestamp(stat.time)
                item.body = stat.message
                item.service = serv
                item.user = user
                item.link_back = 'http://www.facebook.com'
                items.append(item)
    if stats:
        if getattr(links, 'error_code', False):
            raise LoggedServiceError(
            'Facebook service failed to fetch items for causal-user %s, error: %s' % \
                (user.username, results['error_msg'])
            )
        else:
            for link in links:
                if link.has_key('message'):
                    item = ServiceItem()
                    item.created = datetime.fromtimestamp(link.created_time)
                    item.link = True
                    item.body = link.message
                    item.service = serv
                    item.user = user
                    items.append(item)
        
        if getattr(stream, 'error_code', False):
            raise LoggedServiceError(
            'Facebook service failed to fetch items for causal-user %s, error: %s' % \
                (user.username, results['error_msg'])
            )
        else:    
            for strm in stream:
                # do we have permission from the user to post entry?
                # ignore if the post is entry
                if strm['comments']['can_post'] and strm.has_key('message'):
                    if strm.has_key('likes') and strm['likes'].has_key('user_likes'):
                        if strm['likes']['user_likes']:
                            item = ServiceItem()
                            item.liked = strm['likes']['user_likes']
                            item.who_else_liked = strm['likes']['href']
                            item.created = datetime.fromtimestamp(strm.created_time)
                            item.body = strm.message
                            
                            # go off and fetch details about a user
                            item.other_peoples_comments = []
                            for comment in strm['comments']['comment_list']:
                                users = q(USER_NAME_FETCH % comment['fromid'])
                                for user in users:
                                    user_details = {
                                        'name' : user['name'],
                                        'profile_pic' : user['pic_small']
                                    }
                                    item.other_peoples_comments.append(user_details)
                            item.service = serv
                            item.user = user
                            item.link_back = strm['permalink']
                            items.append(item)
    
    return items
