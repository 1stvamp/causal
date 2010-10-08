from datetime import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from causal.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from causal.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name
from django.template import RequestContext
from causal.main.decorators import can_view_service

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        # Now we have a userservice and app create a request token
        request_token = RequestToken(service=service)
        request_token.created = datetime.now()
        request_token.save()

        access_token = AccessToken(service=service)
        access_token.username = username
        access_token.created = datetime.now()
        access_token.api_token = service.app.oauth.consumer_key
        access_token.save()

        service.setup = True
        service.save()

    return redirect(reverse('profile'))

@can_view_service
def stats(request, service_id):
    """Create up some stats."""
    service = get_object_or_404(UserService, pk=service_id)
    
    template_values = {}
    
    return render_to_response(
      service.app.module_name + '/stats.html',
      template_values,
      context_instance=RequestContext(request)
    )