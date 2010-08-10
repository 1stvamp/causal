import cgi
import urllib
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from helios.main.models import AccessToken
from helios.main.service_utils import get_model_instance

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    service = get_model_instance(request.user, __package__)
    code = request.GET.get('code')
    callback = "%s%s" % (service.app.oauth.callback_url_base, reverse('helios-facebook-callback'),)
    url = "%s&code=%s&client_secret=%s&redirect_uri=%s" % (
        service.app.oauth.access_token_url,
        code,
        service.app.oauth.consumer_secret,
        callback,
    )
    response = cgi.parse_qs(urllib.urlopen(url).read())
    access_token = response["access_token"][-1]

    update_attrs = {
        'oauth_token': access_token,
    }
    insert_attrs = {
        'service': service,
    }
    rows = AccessToken.objects.filter(**insert_attrs).update(**update_attrs)
    if not rows:
        insert_attrs.update(update_attrs)
        insert_attrs['created'] = datetime.now()
        AccessToken.objects.create(**insert_attrs)

    return_url = request.session.get('helios_facebook_oauth_return_url', None) or 'history'
    return redirect(return_url)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    request.session['helios_facebook_oauth_return_url'] = request.GET.get('HTTP_REFERER', None)
    service = get_model_instance(request.user, __package__)
    callback = "%s%s" % (service.app.oauth.callback_url_base, reverse('helios-facebook-callback'),)
    return redirect("%s&redirect_uri=%s&scope=%s" % (
            service.app.oauth.request_token_url,
            callback,
            'read_stream',
        )
    )
