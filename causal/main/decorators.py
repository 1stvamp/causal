"""Utility decorators, mainly for wrapping views"""


from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
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
    service = get_object_or_404(UserService, pk=kwargs.get('service_id'))
    if service.share or (request.user.is_authenticated()  and request.user.pk == service.user.pk):
        return True
    else:
        return False
