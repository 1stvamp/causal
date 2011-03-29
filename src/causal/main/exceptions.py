"""Exceptions for use in handling service errors"""

import logging

class ServiceError(Exception):
    """Generic exception for any causal service error, e.g. Twitter is down"""

    original_exception = None

    def __init__(self, *args, **kwargs):
        original = kwargs.get('original_exception', None)
        self.original_exception = original

        if kwargs.has_key('original_exception'):
            del kwargs['original_exception']

        super(ServiceError, self).__init__(*args, **kwargs)

class LoggedServiceError(ServiceError):
    """Wrapper around ServiceError that calls logging.error on init"""

    def __init__(self, *args, **kwargs):
        super(LoggedServiceError, self).__init__(*args, **kwargs)
        if self.original_exception:
            logging.error(repr(self.original_exception))
        else:
            logging.error(repr(self))
