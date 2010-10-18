import httplib2
import oauth2 as oauth
from datetime import datetime
from causal.main.models import ServiceItem, AccessToken
from causal.main.service_utils import get_model_instance
from facegraph.fql import FQL
from causal.main.exceptions import LoggedServiceError

DISPLAY_NAME = 'Facebook'
CUSTOM_FORM = False
OAUTH_FORM = True

SELECT_FQL = """SELECT post_id, actor_id, target_id, updated_time, message
FROM stream
WHERE filter_key IN (
    SELECT filter_key
    FROM stream_filter
    WHERE uid = me() AND type = 'newsfeed'
)
AND (actor_id = me() OR target_id =  me() OR source_id = me())"""

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)

    try:
        q = FQL(at.oauth_token)
        results = q(SELECT_FQL)
    except Exception, e:
        raise LoggedServiceError(original_exception=e)
    
    if getattr(results, 'error_code', False):
        raise LoggedServiceError(
        'Facebook service failed to fetch items for causal-user %s, error: %s' % \
            (user.username, results['error_msg'])
    )

    for result in results:
        item = ServiceItem()
        item.created = datetime.fromtimestamp(result.updated_time)
        item.body = result.message
        item.service = serv
        item.user = user
        items.append(item)

    return items

def get_items_as_json(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    try:
        at = AccessToken.objects.get(service=serv)

        q = FQL(at.oauth_token)
        results = q(SELECT_FQL)

        for result in results:
            item = ServiceItem()
            item.created = datetime.fromtimestamp(result.updated_time)
            item.body = result.message
            item.service = serv
            items.append(item)
    except:
        pass

    return items