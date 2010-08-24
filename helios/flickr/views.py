from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from helios.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from helios.main.service_utils import get_model_instance, user_login, generate_access_token
from datetime import datetime
from django.core.urlresolvers import reverse

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, __name__)
    if not service and request.method == 'POST':
        username = request.POST['username']

        app = ServiceApp.objects.get(module_name=__name__)

        service = UserService(user=request.user, app=app)
        service.save()

        # Now we have a userservice and app create a request token
        request_token = RequestToken(service=service)
        request_token.created = datetime.now()
        request_token.save()

        #http://api.flickr.com/services/rest/?method=flickr.people.findByUsername&api_key=KEY&username=USERNAME
        access_token = AccessToken(service=service)
        access_token.username = username
        access_token.created = datetime.now()
        access_token.api_token = app.oauth.consumer_key
        access_token.save()

    return redirect(reverse('profile'))