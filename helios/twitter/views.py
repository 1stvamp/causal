from django.shortcuts import redirect
from helios.main.models import Service, RequestToken

def verify_auth(request):
    service = Service.objects.get(user=request.user, app_name=__package__)
    request_token = RequestToken.object.get(user=request.user, service=service)
    request_token.oauth_verify = request.GET.get('oauth_verifier')
    request_token.save()
    return_url = request.session.get('helios_twitter_oauth_return_url', None) or 'history'
    return redirect(return_url)