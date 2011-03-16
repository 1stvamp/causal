"""Base service handler classes
"""

class BaseServiceHandler(object):
    def __init__(self, model_instance):
        self.service = model_instance

    def enable(self):
        """Setup and authorise the service."""
        return redirect("%s-auth" % (self.service.app.module_name.replace('.', '-'),))

    def get_items(self, since):
        raise NotImplementedError("ServiceHandler classes need a custom get_items method")
