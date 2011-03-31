"""Handle URLs for the http://foursquare.com service. We are using
full blown oauth to access the user's details.
"""

from causal.main.decorators import can_view_service
from causal.main.models import UserService, RequestToken, ServiceApp, OAuth
from causal.main.utils.services import get_model_instance, user_login, \
     generate_access_token, settings_redirect, check_is_service_id
from causal.main.utils.views import render
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

PACKAGE = 'causal.foursquare'

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    """Handle the redirect from foursquare as part of the oauth process.
    """

    service = get_model_instance(request.user, PACKAGE)
    request_token = service.auth.request_token
    request_token.oauth_verify = request.GET.get('oauth_verifier')
    request_token.save()

    generate_access_token(service, "http://foursquare.com/oauth/access_token")
    service.setup = True
    service.public = True
    service.save()

    return redirect(settings_redirect(request))

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """Setup oauth details for the return call from foursquare.
    """

    request.session['causal_foursquare_oauth_return_url'] = \
           request.GET.get('HTTP_REFERER', None)
    service = get_model_instance(request.user, PACKAGE)

    if not service.auth:
        auth_handler = OAuth()
        auth_handler.save()
        service.auth = auth_handler
        service.save()
    return user_login(service, "http://foursquare.com/oauth/request_token", "http://foursquare.com/oauth/authorize")

@can_view_service
def stats(request, service_id):
    """Display stats based on checkins.
    """

    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, PACKAGE):
        template_values = {}
        # get checkins
        checkins = service.handler.get_items(date.today() - timedelta(days=7))

        template_values['checkins'] = checkins

        return render(
            request,
            template_values,
            'causal/foursquare/stats.html'
        )
    else:
        return redirect('/%s' % (request.user.username,))
