"""Base service handler classes
"""

from django.core.urlresolvers import reverse
from django.shortcuts import redirect

class BaseServiceHandler(object):
    display_name = 'BASE SERVICE HANDLER'
    custom_form = False
    oauth_form = False
    # Don't require enable() to be called by default, this is normally only
    # needed by services that have auth steps, such as enabled OAuth services
    requires_enabling = False

    def __init__(self, model_instance):
        self.service = model_instance

    def get_auth_url_alias(self):
        """Returns the alias to lookup the reversable auth URL, not used by
        most services.
        """
        raise NotImplementedError()

    def get_auth_url(self):
        """Returns the URL to auth the service, not used by most services.
        """
        raise NotImplementedError()

    def get_auth_url_alias(self):
        """Returns the alias to lookup the reversable auth URL.
        """
        return "%s-auth" % (self.service.app.module_name.replace('.', '-'),)

    def get_auth_url(self):
        """Returns the URL to auth the service.
        """
        return reverse(self.get_auth_url_alias())

    def enable(self):
        """Action to enable this service, not needed by most services.
        """
        raise NotImplementedError()

    def get_items(self, since):
        raise NotImplementedError("ServiceHandler classes need a custom get_items method")

class OAuthServiceHandler(BaseServiceHandler):
    oauth_form = True
    requires_enabling = True

    def enable(self):
        """Setup and authorise the service.
        """
        return redirect(self.get_auth_url_alias())
