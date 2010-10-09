from datetime import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from causal.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from causal.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from causal.main.decorators import can_view_service
from causal.github.service import get_items
from datetime import date, timedelta

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        # Delete existing token
        existing_access_token = AccessToken.objects.filter(service=service)
        if existing_access_token:
            existing_access_token.delete()

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
    commits = get_items(request.user, date.today() - timedelta(days=7), service)
    template_values = {'commits': commits}
    
    return render_to_response(
      service.app.module_name + '/stats.html',
      template_values,
      context_instance=RequestContext(request)
    )