import cgi
import urllib
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from causal.main.models import AccessToken, ServiceApp, UserService, RequestToken
from causal.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name

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
    access_token = response["access_token"][-1]
    
    at = AccessToken.objects.filter(service=service).delete()
    new_at = AccessToken()
    new_at.service = service
    new_at.oauth_token = access_token
    new_at.oauth_token_secret = ''
    new_at.created = datetime.now()
    new_at.oauth_verify = ''
    new_at.save()
    
    service.setup = True
    service.save()

    return_url = request.session.get('causal_facebook_oauth_return_url', None) or 'user-settings'
    return redirect(return_url)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    request.session['causal_facebook_oauth_return_url'] = request.GET.get('HTTP_REFERER', None)
    service = get_model_instance(request.user, MODULE_NAME)
    
    callback = "%s%s" % (service.app.oauth.callback_url_base, reverse('causal-facebook-callback'),)
    return redirect("%s&redirect_uri=%s&scope=%s&client_id=%s" % (
            service.app.oauth.request_token_url,
            callback,
            'read_stream',
            service.app.oauth.consumer_key
        )
    )
