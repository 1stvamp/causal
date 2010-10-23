from django.conf import settings

def config(context):
    """Provide access to the values such as ENABLE_REGISTRATION
    """
    return {'ENABLE_REGISTRATION': settings.ENABLE_REGISTRATION}
