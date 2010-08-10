import httplib2
import oauth2 as oauth
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
from helios.main.models import ServiceItem, AccessToken
from helios.main.service_utils import get_model_instance
from facegraph.fql import FQL

display_name = 'Facebook'

SELECT_FQL = """SELECT post_id, actor_id, target_id, message
FROM stream
WHERE filter_key
IN (
    SELECT filter_key
    FROM stream_filter
    WHERE uid = %%s AND type = 'newsfeed'
)"""

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __package__)
    items = []

    try:
        at = AccessToken.object.get(service=serv)

        q = FQL(serv.app.oauth.consumer_secret)
        results = q(SELECT_FQL % (at.username,))

        for result in results:
            item = ServiceItem()
            item.body = result.message
            item.service = serv
            items.append(item)
    except:
        pass

    return items
