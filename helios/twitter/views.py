from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from helios.main.models import UserService, RequestToken
from helios.twitter.utils import user_login
from helios.main.service_utils import get_model_instance

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    service = get_model_instance(request.user, __name__)
    request_token = RequestToken.objects.get(service=service)
    request_token.oauth_verify = request.GET.get('oauth_verifier')
    request_token.save()
    return_url = request.session.get('helios_twitter_oauth_return_url', None) or 'history'
    return redirect(return_url)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    request.session['helios_twitter_oauth_return_url'] = request.GET.get('HTTP_REFERER', None)
    return user_login(get_model_instance(request.user, __name__))
