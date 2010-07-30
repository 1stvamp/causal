from django.shortcuts import redirect
from helios.main.models import UserService, RequestToken
from helios.twitter.utils import get_model_instance

def verify_auth(request):
    service = get_model_instance(request.user)
    request_token = RequestToken.object.get(user=request.user, service=service)
    request_token.oauth_verify = request.GET.get('oauth_verifier')
    request_token.save()
    return_url = request.session.get('helios_twitter_oauth_return_url', None) or 'history'
    return redirect(return_url)