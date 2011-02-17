import re
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

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

@register.filter
def only_setup(qs):
    """Filter a given UserService queryset for only fully setup services
    """
    return qs.filter(setup=True)

@register.filter
def stats_url(service):
    """Return the URL for a service's stats ''if it has one''
    """
    try:
        # uses the urls.py from the app's own directory
        return reverse('%s-stats' % (service.class_name,), kwargs={'service_id': service.pk})
    except NoReverseMatch:
        return False
