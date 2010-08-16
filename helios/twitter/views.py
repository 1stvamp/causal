from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from helios.main.models import UserService, RequestToken, OAuthSetting, ServiceApp
from helios.twitter.utils import user_login
from helios.main.service_utils import get_model_instance, generate_access_token

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    service = get_model_instance(request.user, __name__)
    request_token = RequestToken.objects.get(service=service)
    request_token.oauth_verify = request.GET.get('oauth_verifier')
    request_token.save()
    generate_access_token(service, request_token)
    return_url = request.session.get('helios_twitter_oauth_return_url', None) or 'history'
    return redirect(return_url)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    request.session['helios_twitter_oauth_return_url'] = request.GET.get('HTTP_REFERER', None)
    try: 
        # try and get twitter stuff
        # this will fail first time round as we have auth from the user
        # so lets set it up
        model = get_model_instance(request.user, __package__)
    except:
        oauth_setting = OAuthSetting.objects.get(name=__package__.split('.')[1])
        app = ServiceApp(module_name=__package__, oauth=oauth_setting)
        app.save()
        service = UserService(user=request.user, app=app)
        service.save()
        model = get_model_instance(request.user, __package__)
    return user_login(model)
