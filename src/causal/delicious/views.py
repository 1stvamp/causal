"""Handles user accessable urls for http://delicious.com service.
There isn't an easy to user API for this service so we work on
publicly rss feeds from the user's account.
"""

from causal.main.models import UserService, Auth
from causal.main.utils.services import get_model_instance, \
        settings_redirect, check_is_service_id, get_data
from causal.main.utils.views import render
from causal.main.decorators import can_view_service
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

PACKAGE_NAME = 'causal.delicious'

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""

    service = get_model_instance(request.user, PACKAGE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        if username:
            user_feed = get_data(
                service,
                'http://feeds.delicious.com/v2/json/%s' % (username,),
                disable_oauth=True
            )

            # check the username is valid
            if user_feed[0]['d'] == '404 Not Found':
                messages.error(request, 'Unable to find username "%s", please try again' % (username,))
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
            messages.error(request, 'Please enter a Delicious username')

    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Create up some stats.
    """

    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, PACKAGE_NAME):
        bookmarks = service.handler.get_items(date.today() - timedelta(days=7))

        tags = {}

        for bookmark in bookmarks:
            for tag in bookmark.tags:
                if tags.has_key(tag):
                    tags[tag] = tags[tag] + 1
                else:
                    tags[tag] = 1

        return render(
            request,
            {
                'bookmarks': bookmarks,
                'tags' : tags
            },
            'causal/delicious/stats.html'
        )
    else:
        return redirect('/%s' % (request.user.username,))
