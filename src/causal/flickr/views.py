"""Handle account settings for flickr and other direct url requests."""

from causal.flickr.service import get_items
from causal.main.decorators import can_view_service
from causal.main.models import UserService, RequestToken, OAuthSetting, ServiceApp, AccessToken
from causal.main.service_utils import get_model_instance, user_login, generate_access_token, get_module_name
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import httplib2
from lxml import etree

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    service = get_model_instance(request.user, MODULE_NAME)
    
    if service and request.method == 'POST':
        username = request.POST['username']
        
        # talk to flickr to get a flickr ID 1234567@N0 style
        url = "http://api.flickr.com/services/rest/?method=flickr.people.findByUsername&api_key=%s&username=%s" % \
            (service.app.oauth.consumer_key, username)
        
        h = httplib2.Http()
        resp, content = h.request(url, "GET")
        
        # parse the request and check we have got back flickr id
        try:
            tree = etree.fromstring(content)
            userid = tree.xpath('/rsp/user')[0].get('id')
              
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
        except:
            messages.error(request, 'Unable to validate your username with Flickr, please check your username and retry.')
            redirect(reverse('user-settings'))

    return redirect(reverse('user-settings'))

@can_view_service
def stats(request, service_id):
    """Create up some stats."""
    service = get_object_or_404(UserService, pk=service_id)
    pictures = get_items(request.user, date.today() - timedelta(days=7), service)
    template_values = {}
    # most commented
    comments = 0
    template_values['most_commented_picture'] = None
    template_values['number_of_pictures_favorites'] = 0
    for pic in pictures:

        if pic.has_location():
            template_values['pic_centre'] = pic
        
        if pic.favorite:
            template_values['number_of_pictures_favorites'] = number_of_pictures_favorites + 1
        if int(pic.number_of_comments) > 0:
            if pic.number_of_comments > comments:
                comments = pic.number_of_comments
                template_values['most_commented_picture'] = pic
        
        template_values['pictures'] = pictures
        template_values['number_of_pictures_uploaded'] = len(pictures)
    
    return render_to_response(
        service.template_name + '/stats.html',
        template_values,
        context_instance=RequestContext(request)
    )
