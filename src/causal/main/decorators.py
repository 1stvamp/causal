"""Utility decorators, mainly for wrapping views"""


from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page as _cache_page
from django.conf import settings
from causal.main.models import UserService

def permission(permission_tester):
    """Decorator to easilly allow other decorators to provide permission
    checks on views.
    """
    def view_decorator(view_function):
        def decorated_view(request, *args, **kwargs):
            if permission_tester(request, *args, **kwargs):
                view_result = view_function(request, *args, **kwargs)
            else:
                if request.user.is_authenticated():
                    view_result = HttpResponseNotAllowed('Permission denied')
                else:
                    view_function_decorated = login_required(view_function)
                    view_result = view_function_decorated(request, *args, **kwargs)

            return view_result
        return decorated_view
    return view_decorator

@permission
def can_view_service(request, *args, **kwargs):
    """Wrapper for login_required decorator to only allow viewing service
    if service is shared or user is logged in as service owner.
    """
    service = get_object_or_404(UserService, pk=kwargs.get('service_id'))
    if service.share or (request.user.is_authenticated()  and request.user.pk == service.user.pk):
        return True
    else:
        return False

def cache_page(f, *args, **kwargs):
    """Version of the cache_page decorator that does not return a cache
    if ENABLE_CACHING is set to False in the settings module. Means
    the decorator can be used regardless of cache availability.
    """
    if getattr(settings, 'ENABLE_CACHING', True):
        return _cache_page(f, *args, **kwargs)
    else:
        return f
