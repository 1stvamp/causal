"""Handles all the user accessable pages for the Tumblr App.
There is a basic API at http://tumblr.com.

Everything done is from the publicly rss feeds from the users account
which is how the API works."""

from causal.main.decorators import can_view_service
from causal.main.models import UserService, AccessToken
from causal.main.utils import get_module_name
from causal.main.utils.services import get_model_instance, settings_redirect, \
     check_is_service_id
from causal.tumblr.service import get_items
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

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

    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Create up some stats."""

    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, MODULE_NAME):
        try:
            posts = get_items(request.user,
                              date.today() - timedelta(days=7), service)
        except:
            messages.error(request, 'There was an error connnecting to Tumblr.')

        return render(
            request,
            {'posts': posts},
            service.template_name + '/stats.html'
        )
    else:
        return redirect('/%s' %(request.user.username))
