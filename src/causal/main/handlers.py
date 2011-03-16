"""Base service handler classes
"""

class BaseServiceHandler(object):
    display_name = 'BASE SERVICE HANDLER'
    custom_form = False
    oauth_form = False
    # Don't require enable() to be called by default, this is normally only
    # needed by services that have auth steps, such as enabled OAuth services
    requires_enabling = False

    def __init__(self, model_instance):
        self.service = model_instance

    def enable(self):
        """Setup and authorise the service."""
        return redirect("%s-auth" % (self.service.app.module_name.replace('.', '-'),))

    def get_items(self, since):
        raise NotImplementedError("ServiceHandler classes need a custom get_items method")
