"""Exceptions for use in handling service errors"""

class ServiceError(Exception):

    original_exception = None

    def __init__(self, *args, **kwargs):
        original = kwargs.get('original_exception', None)
        original_exception = original

        if kwargs.has_key('original_exception'):
            del kwargs['original_exception']

        super(ServiceError, self).__init__(*args, **kwargs)

