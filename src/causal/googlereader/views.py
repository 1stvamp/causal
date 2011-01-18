"""Handles all the user accessable pages for the Google Reader App.
At present Google Reader (http://reader.google.com) lacks any API support.

Everything done is from the publicly rss feeds from the users account."""

from BeautifulSoup import Tag, BeautifulSoup as soup
from BeautifulSoup import SoupStrainer
from causal.googlereader.service import get_items
from causal.main.models import UserService, AccessToken
from causal.main.service_utils import get_model_instance, get_module_name, settings_redirect
from causal.main.decorators import can_view_service
from datetime import datetime, date, timedelta
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.datastructures import SortedDict
import httplib2

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    if service and request.method == 'POST':
        username = request.POST['username']

        # fetch the page and try to find the reader id
        url = "http://www.google.com/reader/shared/%s" % username
        links = SoupStrainer('link')
        h = httplib2.Http()
        resp, content = h.request(url, "GET")
        parsed_links = [tag for tag in soup(str(content), parseOnlyThese=links)]
        userid = parsed_links[2].attrs[2][1].split('%2F')[1]
        # Delete existing token
        AccessToken.objects.filter(service=service).delete()
        # Before creating a new one
        AccessToken.objects.create(
            service=service,
            username=username,
            userid=userid,
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
    shares = get_items(request.user, date.today() - timedelta(days=7), service)
    sources = {}

    # count source websites
    for share in shares:
        if sources.has_key(share.source):
            sources[share.source] = sources[share.source] + 1
        else:
            sources[share.source] = 1

    sources = SortedDict(sorted(sources.items(), 
                                reverse=True, key=lambda x: x[1]))
    sources_reversed = SortedDict(sorted(sources.items(), 
                                reverse=False, key=lambda x: x[1]))
    
    return render_to_response(
        service.template_name + '/stats.html',
        {'shares' : shares,
         'sources' : sources,
         'sources_reversed' : sources_reversed},
        context_instance=RequestContext(request)
    )
