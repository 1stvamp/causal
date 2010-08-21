from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from helios.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from helios.main.service_utils import get_model_instance, user_login, generate_access_token
from datetime import datetime
from django.core.urlresolvers import reverse

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    model = get_model_instance(request.user, __package__)
    if not model and request.method == 'POST':
        username = request.POST['username']
        oauth_setting = OAuthSetting.objects.get(name=__package__.split('.')[1])
        
        app = ServiceApp(module_name=__package__, oauth=oauth_setting)
        app.save()
        
        service = UserService(user=request.user, app=app)
        service.save()
        
        # now we have a userservice and app create a request token
        request_token = RequestToken(service=service)
        request_token.created = datetime.now()
        request_token.save()
        
        access_token = AccessToken(service=service)
        access_token.username = username
        access_token.created = datetime.now()
        access_token.api_token = oauth_setting.consumer_key
        access_token.save()
        
    return redirect(reverse('profile'))