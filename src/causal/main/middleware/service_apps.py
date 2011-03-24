"""Middleware for the maintenance of Causal ServiceApps
"""

from causal.main.models import get_app_by_name, ServiceApp
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

class SetupServiceApps(object):
    def __init__(self):
        # Make sure we have a corresponding ServiceApp model instance for each
        # installed service
        for module_name in settings.INSTALLED_SERVICES:
            app = get_app_by_name(module_name)
            if not app.enable:
                app.enable = True
                app.save()
        # Disable any ServiceApp not installed
        ServiceApp.objects.exclude(module_name__in=settings.INSTALLED_SERVICES).update(enable=False)
        raise MiddlewareNotUsed()
