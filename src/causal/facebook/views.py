import cgi
import urllib
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from causal.main.models import AccessToken, ServiceApp, UserService, RequestToken
from causal.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name
from django.shortcuts import render_to_response, get_object_or_404
from causal.facebook.service import get_items
from datetime import date, timedelta
from causal.main.decorators import can_view_service
from django.contrib import messages
from django.template import RequestContext

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    service = get_model_instance(request.user, MODULE_NAME)
    code = request.GET.get('code')
    callback = "%s%s" % (service.app.oauth.callback_url_base, reverse('causal-facebook-callback'),)
    url = "%s&code=%s&client_secret=%s&redirect_uri=%s" % (
        service.app.oauth.access_token_url,
        code,
        service.app.oauth.consumer_secret,
        callback,
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
        
    return_url = request.session.get('causal_facebook_oauth_return_url', None) or 'user-settings'
    
    return redirect(return_url)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    request.session['causal_facebook_oauth_return_url'] = request.GET.get('HTTP_REFERER', None)
    service = get_model_instance(request.user, MODULE_NAME)

    if not service:
        app = ServiceApp.objects.get(module_name=MODULE_NAME)
        service = UserService(user=request.user, app=app)
        service.save()
    callback = "%s%s" % (service.app.oauth.callback_url_base, reverse('causal-facebook-callback'),)
    return redirect("%s&redirect_uri=%s&scope=%s&client_id=%s" % (
            service.app.oauth.request_token_url,
            callback,
            'read_stream,offline_access',
            service.app.oauth.consumer_key
        )
    )
        
@can_view_service
def stats(request, service_id):
    """Display stats based on checkins."""
    service = get_object_or_404(UserService, pk=service_id)
    
    return render_to_response(
        service.template_name + '/stats.html',
        {'statuses' : get_items(request.user, date.today() - timedelta(days=7), service, True)},
        context_instance=RequestContext(request)
    )
