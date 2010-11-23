from datetime import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from causal.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from causal.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name
from datetime import date, timedelta
from causal.lastfm.service import get_items, get_artists, get_upcoming_gigs
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from causal.main.decorators import can_view_service
from causal.main.service_utils import get_model_instance, get_data

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

    return redirect(reverse('user-settings'))

@can_view_service
def stats(request, service_id):
    """Display stats based on checkins."""
    service = get_object_or_404(UserService, pk=service_id)
    template_values = {}

    template_values['favourite_artists'] = get_artists(request.user, date.today() - timedelta(days=7), service)
    template_values['recent_tracks'] = get_items(request.user, date.today() - timedelta(days=7), service)
    
    for artist in template_values['favourite_artists']:
        artist.gigs = get_upcoming_gigs(request.user, date.today() - timedelta(days=7), service, artist.name)
        if artist.gigs:
            template_values['gig_centre'] = artist.gigs[0]
        
    return render_to_response(
        service.template_name + '/stats.html',
        template_values,
        context_instance=RequestContext(request)
    )
