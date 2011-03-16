"""Middleware for the maintenance of Causal ServiceApps
"""

from causal.main.models import get_app_by_name
from django.config import settings
from django.core.exceptions import MiddlewareNotUsed

class SetupServiceApps(object):
    def __init__(self):
        # Make sure we have a corresponding ServiceApp model instance for each
        # installed service
        for module_name in settings.INSTALLED_SERVICES:
            get_app_by_name(module_name)
        raise MiddlewareNotUsed()
