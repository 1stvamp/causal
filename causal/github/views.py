from datetime import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from helios.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from helios.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        # Now we have a userservice and app create a request token
        request_token = RequestToken(service=service)
        request_token.created = datetime.now()
        request_token.save()

        access_token = AccessToken(service=service)
        access_token.username = username
        access_token.created = datetime.now()
        access_token.api_token = service.app.oauth.consumer_key
        access_token.save()

        service.setup = True
        service.save()

    return redirect(reverse('profile'))
