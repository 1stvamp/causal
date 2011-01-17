"""Handles user accessable urls for http://delicious.com service.
There isn't an easy to user API for this service so we work on
publicly rss feeds from the user's account."""

from causal.main.models import UserService, AccessToken
from causal.main.service_utils import get_model_instance, \
get_module_name, settings_redirect
from causal.main.decorators import can_view_service
from causal.delicious.service import get_items
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        # Delete existing token
        AccessToken.objects.filter(service=service).delete()
        # Before creating a new one
        AccessToken.objects.create(
            service=service,
            username=username,
            created=datetime.now(),
            api_token=service.app.oauth.consumer_key
        )

        service.setup = True
        service.public = True
        service.save()

    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Create up some stats."""
    service = get_object_or_404(UserService, pk=service_id)
    commits = get_items(request.user, date.today() - timedelta(days=7), service)
    return render_to_response(
        service.template_name + '/stats.html',
        {'commits': commits},
        context_instance=RequestContext(request)
    )
