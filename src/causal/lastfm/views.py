""" Handles requests for the http://last.fm service.
We only access public feeds for the user. There is a full blown "oauth"
interface but we don't need to use it.
"""

from datetime import datetime
from causal.main.decorators import can_view_service
from causal.main.models import UserService, Auth
from causal.main.utils.services import get_model_instance, \
        settings_redirect, check_is_service_id, get_data
from causal.main.utils.views import render
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

PACKAGE_NAME = 'causal.lastfm'

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username.
    """
    service = get_model_instance(request.user, PACKAGE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        if username:
            user_feed = get_data(
                service,
                'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json'  % (
                    username,
                    service.app.auth_settings['api_key']
                ),
                disable_oauth=True
            )

            # check we have a valid username
            if not user_feed.has_key('error') or (
              user_feed.has_key('error') and user_feed['error'] != 6):
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
                messages.error(
                    request,
                    'Unable to validate your username "%s" with Last.fm, please check your username and retry.' % (
                        username,
                    )
                )

        else:
            messages.error(request, 'Please enter a Last.fm username')

    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Display stats based on checkins.
    """
    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, PACKAGE_NAME):
        template_values = {}

        date_offset = date.today() - timedelta(days=7)

        template_values['favourite_artists'] = service.handler.get_artists(date_offset)
        template_values['recent_tracks'] = service.handler.get_items(date_offset)

        gig_index = 0

        for artist in template_values['favourite_artists']:
            artist.gigs = service.handler.get_upcoming_gigs(date_offset, artist.name)
            if artist.gigs:
                if not template_values.has_key('gig_centre') and \
                   artist.gigs[gig_index].location.has_key('lat') and \
                   artist.gigs[gig_index].location.has_key('long') and \
                   artist.gigs[gig_index].location['lat'] and \
                   artist.gigs[gig_index].location['long']:
                    template_values['gig_centre'] = artist.gigs[0]
                else:
                    gig_index = gig_index + 1

        return render(
            request,
            template_values,
            'causal/lastfm/stats.html'
        )
    else:
        return redirect('/%s' % (request.user.username,))
