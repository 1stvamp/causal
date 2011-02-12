"""Deals with all the user accessable urls for http://facebook.com.
This service requires we use a facegraph python lib. Most of
the stats work is done using FQL."""

import cgi
import urllib
from causal.facebook.service import get_items, get_stats_items
from causal.main.decorators import can_view_service
from causal.main.models import AccessToken, ServiceApp, UserService
from causal.main.utils import get_module_name
from causal.main.utils.services import get_model_instance, settings_redirect, \
        check_is_service_id
from causal.main.utils.views import render
from datetime import datetime, date, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    """Get the values back from facebook and store them for use later."""

    service = get_model_instance(request.user, MODULE_NAME)
    code = request.GET.get('code')
    callback = "%s%s" % (service.app.oauth.callback_url_base,
                         reverse('causal-facebook-callback'),)
    url = "%s&code=%s&client_secret=%s&redirect_uri=%s&client_id=%s" % (
        service.app.oauth.access_token_url,
        code,
        service.app.oauth.consumer_secret,
        callback,
        service.app.oauth.consumer_key
    )

    response = cgi.parse_qs(urllib.urlopen(url).read())

    if response.has_key('access_token'):
        # Delete existing token
        AccessToken.objects.filter(service=service).delete()
        # Before creating a new one
        AccessToken.objects.create(
            service=service,
            oauth_token=''.join(response["access_token"]),
            oauth_token_secret='',
            created=datetime.now(),
            oauth_verify=''
        )
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
    service = get_model_instance(request.user, MODULE_NAME)

    if not service:
        app = ServiceApp.objects.get(module_name=MODULE_NAME)
        service = UserService(user=request.user, app=app)
        service.save()
    callback = "%s%s" % (service.app.oauth.callback_url_base,
                         reverse('causal-facebook-callback'),)
    return redirect("%s&redirect_uri=%s&scope=%s&client_id=%s" % (
            service.app.oauth.request_token_url,
            callback,
            'read_stream,offline_access,user_photos,user_photo_video_tags,user_checkins',
            service.app.oauth.consumer_key
        )
    )

@can_view_service
def stats(request, service_id):
    """Display stats based on checkins."""

    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, MODULE_NAME):
        links, statuses, details, photos, checkins = get_stats_items(request.user, date.today() - timedelta(days=7), service)
        return render(
            request,
            {'links' : links,
             'statuses' : statuses,
             'details' : details,
             'photos': photos,
             'checkins' : checkins,
             },
            service.template_name + '/stats.html'
        )
    else:
        return redirect('/%s' %(request.user.username))
