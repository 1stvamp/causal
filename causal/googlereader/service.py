import time
import feedparser
from dateutil import parser
from datetime import datetime
from causal.main.models import AccessToken, ServiceItem
from causal.main.service_utils import get_model_instance
from causal.main.exceptions import LoggedServiceError

DISPLAY_NAME = 'Google Reader'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance=None):
    pass

def get_items_as_json(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user, __name__)
    pass
