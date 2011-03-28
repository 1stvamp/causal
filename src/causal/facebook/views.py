"""Deals with all the user accessable urls for http://facebook.com.
This service requires we use a facegraph python lib. Most of
the stats work is done using FQL."""

import cgi
import urllib
from causal.main.decorators import can_view_service
from causal.main.models import AccessToken, ServiceApp, UserService, OAuth
from causal.main.utils.services import get_model_instance, settings_redirect, \
        check_is_service_id, get_config
from causal.main.utils.views import render
from datetime import datetime, date, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

PACKAGE = 'causal.facebook'

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    """Get the values back from facebook and store them for use later."""

    service = get_model_instance(request.user, PACKAGE)
    code = request.GET.get('code')
    if request.is_secure():
        scheme = "https://"
    else:
        scheme = "http://"
    base_url = "%s%s" % (scheme, request.get_host(),)
    callback = "%s%s" % (base_url, reverse('causal-facebook-callback'),)

    url = "https://graph.facebook.com/oauth/access_token&code=%s&client_secret=%s&redirect_uri=%s&client_id=%s" % (
        code,
        service.app.auth_settings['consumer_secret'],
        callback,
        service.app.auth_settings['consumer_key']
    )

    response = cgi.parse_qs(urllib.urlopen(url).read())

    if response.has_key('access_token'):
        at = AccessToken.objects.create(
            oauth_token=''.join(response["access_token"]),
            oauth_token_secret='',
            oauth_verify=''
        )
        service.auth.access_token = at
        service.auth.save()
        service.setup = True
        service.public = True
        service.save()
        messages.success(request, 'Connection to Facebook complete.')

    else:
        messages.error(request, 'There was an error connnecting to Facebook.')

    return redirect(settings_redirect(request))

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """First leg of the two stage auth process. We setup and take note"""

    request.session['causal_facebook_oauth_return_url'] = \
        request.GET.get('HTTP_REFERER', None)
    service = get_model_instance(request.user, PACKAGE)

    if not service.auth:
        auth_handler = OAuth()
        auth_handler.save()
        service.auth = auth_handler
        service.save()

    if request.is_secure():
        scheme = "https://"
    else:
        scheme = "http://"
    base_url = "%s%s" % (scheme, request.get_host(),)
    callback = "%s%s" % (base_url, reverse('causal-facebook-callback'),)
    return redirect("https://graph.facebook.com/oauth/authorize&redirect_uri=%s&scope=%s&client_id=%s" % (
            callback,
            'read_stream,offline_access,user_photos,user_photo_video_tags,user_checkins',
            service.app.auth_settings['consumer_key']
        )
    )

@can_view_service
def stats(request, service_id):
    """Display stats based on checkins."""

    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, PACKAGE):
        links, statuses, details, photos, checkins = service.handler.get_stats_items(date.today() - timedelta(days=7))
        return render(
            request,
            {'links' : links,
             'statuses' : statuses,
             'details' : details,
             'photos': photos,
             'checkins' : checkins,
             },
            'causal/facebook/stats.html'
        )
    else:
        return redirect('/%s' %(request.user.username))
