import httplib2
import oauth2 as oauth
from datetime import datetime
from django.utils.safestring import mark_safe
from helios.main.models import ServiceItem, AccessToken
from helios.main.service_utils import get_model_instance
from facegraph.fql import FQL

display_name = 'Facebook'

SELECT_FQL = """SELECT post_id, actor_id, target_id, updated_time, message
FROM stream
WHERE filter_key IN (
    SELECT filter_key
    FROM stream_filter
    WHERE uid = me() AND type = 'newsfeed'
)
AND (actor_id = me() OR target_id =  me() OR source_id = me())"""

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __package__)
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
    except Exception, e:
        print e

    return items
