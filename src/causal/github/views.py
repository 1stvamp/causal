""" Handler for URLs for the http://github.com service.
GitHub doesn't really have a decent oauth service so again we
are hitting public json feeds and processing those.
"""

from datetime import datetime
from causal.main.decorators import can_view_service
from causal.main.models import UserService, Auth
from causal.main.utils.services import get_model_instance, \
        settings_redirect, check_is_service_id, get_data
from causal.main.utils.views import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from datetime import date, timedelta

PACKAGE = 'causal.github'

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username.
    """

    service = get_model_instance(request.user, PACKAGE)
    if service and request.method == 'POST':
        username = request.POST['username']

        if username:
            try:
                user_feed = get_data(
                    service,
                    'http://github.com/%s.json' % (username),
                    disable_oauth=True
                )[0]
            except IndexError:
                user_feed = {'error': True}

            # Check the username is valid
            if user_feed.has_key('error'):
                messages.error(request,
                               'Unable to validate your username with Git Hub, please check your username and retry.')
            else:
                if not service.auth:
                    auth_handler = Auth()
                else:
                    auth_handler = service.auth
                auth_handler.username = username
                auth_handler.save()
                if not service.auth:
                    service.auth = auth_handler
                service.setup = True
                service.public = True
                service.save()
        else:
            messages.error(request, 'Please enter a GitHub username')

    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Create up some stats.
    """

    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, PACKAGE):
        commits, avatar, commit_times = service.handler.get_stats_items(date.today() - timedelta(days=7))

        return render(
            request,
            {
                'commits': commits,
                'avatar' : avatar,
                'commit_times' : commit_times
            },
            'causal/github/stats.html'
        )
    else:
        return redirect('/%s' % (request.user.username,))
