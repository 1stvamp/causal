from django import template
from django.conf import settings
from django import template
import re

NUMERIC_TEST = re.compile(r'^\d+$')

register = template.Library()

@register.simple_tag
def setting(name):
    """Tag that provides access to properties from the django.settings
    dictionary.
    Usage:
    {% setting KEY %}
    where KEY is the key in the dictionary you want
    Values are returned as strings.
    """
    return str(settings.__getattr__(name))

@register.filter
def get(value, arg):
    """Gets an attribute of an object dynamically from a string name"""

    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif NUMERIC_TEST.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID
