"""Handles all the user accessable pages for the Google Reader App.
At present Google Reader (http://reader.google.com) lacks any API support.

Everything done is from the publicly rss feeds from the users account."""

import httplib2
from BeautifulSoup import Tag, SoupStrainer, BeautifulSoup as soup
from causal.main.decorators import can_view_service
from causal.main.utils.services import get_model_instance, \
        settings_redirect, check_is_service_id
from causal.main.utils.views import render
from causal.main.models import UserService, Auth
from datetime import datetime, date, timedelta
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.utils.datastructures import SortedDict

# Yay, let's recreate __package__ for Python <2.6
PACKAGE_NAME = 'causal.googlereader'

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username.
    """
    service = get_model_instance(request.user, PACKAGE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        if username:
            # Fetch the page and try to find the reader id
            url = "http://www.google.com/reader/shared/%s" % (username,)
            links = SoupStrainer('link')
            h = httplib2.Http()
            resp, content = h.request(url, "GET")
            parsed_links = [tag for tag in soup(str(content), parseOnlyThese=links)]

            if parsed_links:
                try:
                    user_id = parsed_links[2].attrs[2][1].split('%2F')[1]

                    if not service.auth:
                        auth_handler = Auth()
                    else:
                        auth_handler = service.auth
                    auth_handler.username = username
                    auth_handler.secret = user_id
                    auth_handler.save()
                    if not service.auth:
                        service.auth = auth_handler

                    service.setup = True
                    service.public = True
                    service.save()
                except:
                    messages.error(
                        request,
                        'Unable to find Google Reader account with username "%s"' % (username,)
                    )
            else:
                messages.error(
                    request,
                    'Unable to find Google Reader account with username "%s"' % (username,)
                )
        else:
            messages.error(request, "Please enter a Google Reader username")

    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Create up some stats.
    """

    service = get_object_or_404(UserService, pk=service_id)

    if check_is_service_id(service, PACKAGE_NAME):
        shares = service.handler.get_items(date.today() - timedelta(days=7))
        sources = {}

        # Count source websites
        for share in shares:
            if sources.has_key(share.source):
                sources[share.source] = sources[share.source] + 1
            else:
                sources[share.source] = 1

        sources = SortedDict(
            sorted(sources.items(), reverse=True, key=lambda x: x[1])
        )

        return render(
            request,
            {
                'shares' : shares,
                'sources' : sources,
            },
            'causal/googlereader/stats.html'
        )
    else:
        return redirect('/%s' % (request.user.username,))
