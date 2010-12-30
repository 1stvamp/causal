from datetime import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from causal.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from causal.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from causal.main.decorators import can_view_service
from causal.tumblr.service import get_items
from datetime import date, timedelta
from BeautifulSoup import BeautifulSoup, SoupStrainer

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        # Delete existing token
        AccessToken.objects.filter(service=service).delete()
        # Before creating a new one
        AccessToken.objects.create(
            service=service,
            username=username,
            created=datetime.now(),
            api_token=service.app.oauth.consumer_key
        )

        service.setup = True
        service.public = True
        service.save()

    return redirect(reverse('user-settings'))

@can_view_service
def stats(request, service_id):
    """Create up some stats."""
    service = get_object_or_404(UserService, pk=service_id)
    try:
        posts = get_items(request.user, date.today() - timedelta(days=7), service)
    except:
        messages.error(request, 'There was an error connnecting to Tumblr.')
        
    return render_to_response(
        service.template_name + '/stats.html',
        {'posts': posts},
        context_instance=RequestContext(request)
    )
