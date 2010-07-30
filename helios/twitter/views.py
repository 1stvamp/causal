from django.shortcuts import redirect

def verify_auth(request):
    request.session['helios_twitter_oauth_verify_token'] = request.GET.get('oauth_verifier')
    return_url = request.session.get('helios_twitter_oauth_return_url', None) or 'history'
    return redirect(return_url)