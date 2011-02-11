""" Handler for URLs for the http://github.com service.
GitHub doesn't really have a decent oauth service so again we
are hitting public rss feeds and processing those.
"""

from datetime import datetime
from causal.github.service import get_items, get_stats_items
from causal.main.decorators import can_view_service
from causal.main.models import UserService, AccessToken
from causal.main.utils import get_module_name
from causal.main.utils.services import get_model_instance, \
        settings_redirect, check_is_service_id
from causal.main.utils.views import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
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

    if check_is_service_id(service, MODULE_NAME):
        commits, avatar, commit_times = get_stats_items(request.user, date.today() - timedelta(days=7), service)

        return render(
            request,
            {'commits': commits,
             'avatar' : avatar,
             'commit_times' : commit_times},
            service.template_name + '/stats.html'
        )
    else:
        return redirect('/%s' %(request.user.username))
