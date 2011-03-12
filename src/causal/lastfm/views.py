""" Handles requests for the http://last.fm service.
We only access public feeds for the user. There is a full blown "oauth"
interface but we don't need to use it.
"""

from datetime import datetime
from causal.lastfm.service import get_items, get_artists, get_upcoming_gigs
from causal.main.decorators import can_view_service
from causal.main.models import UserService, AccessToken
from causal.main.utils import get_module_name
from causal.main.utils.services import get_model_instance, \
        settings_redirect, check_is_service_id, get_data
from causal.main.utils.views import render
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        if username:
            # Delete existing token
            AccessToken.objects.filter(service=service).delete()
            
            user_feed = get_data(
                            None,
                            'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json'  % (username, service.app.oauth.consumer_key),
                            disable_oauth=True)
            
            # check we have a valid username
            if not user_feed.has_key('error') and user_feed['error'] != 6:
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
                
            else:
                messages.error(request, 
                               'Unable to validate your username with Last.fm, please check your username and retry.')

        else:
            messages.error(request, 'Please enter a Last.fm username')

    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Display stats based on checkins."""
    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, MODULE_NAME):
        template_values = {}

        date_offset = date.today() - timedelta(days=7)

        template_values['favourite_artists'] = get_artists(request.user,
                                                           date_offset,
                                                           service)
        template_values['recent_tracks'] = get_items(request.user,
                                                     date_offset,
                                                     service)

        gig_index = 0

        for artist in template_values['favourite_artists']:
            artist.gigs = get_upcoming_gigs(request.user,
                                            date.today() - timedelta(days=7),
                                            service,
                                            artist.name)
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
            service.template_name + '/stats.html'
        )
    else:
        return redirect('/%s' %(request.user.username))
