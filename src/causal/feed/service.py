import feed
from datetime import datetime
from django.utils import simplejson
from causal.main.models import ServiceItem, AccessToken
from causal.main.service_utils import get_model_instance
from causal.main.exceptions import LoggedServiceError

DISPLAY_NAME = 'Feed'
CUSTOM_FORM = True
OAUTH_FORM = False

def get_items(user, since, model_instance):
    # FIXME!
    pass