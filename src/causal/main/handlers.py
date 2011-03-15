"""Base service handler classes
"""

class BaseServiceHandler(object):
    def __init__(self, model_instance):
        self.user_service = model_instance

    def enable(self):
        """Setup and authorise the service."""
        return redirect(self.setup_uri)

    def get_items(self, since):
        raise NotImplementedError("ServiceHandler classes need a custom get_items method")
