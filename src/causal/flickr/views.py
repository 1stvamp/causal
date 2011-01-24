"""Handle account settings for flickr and other direct url requests."""

from causal.flickr.service import get_items
from causal.main.decorators import can_view_service
from causal.main.models import UserService, AccessToken
from causal.main.service_utils import settings_redirect, \
     get_model_instance, get_module_name
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils import simplejson
import httplib2

# Yay, let's recreate __package__ for Python <2.6
MODULE_NAME = get_module_name(__name__)

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username."""
    
    service = get_model_instance(request.user, MODULE_NAME)
    
    if service and request.method == 'POST':
        username = request.POST['username']
        
        # talk to flickr to get a flickr ID 1234567@N0 style
        url = "http://api.flickr.com/services/rest/?method=flickr.people.findByUsername&api_key=%s&username=%s&format=json&nojsoncallback=1" % \
            (service.app.oauth.consumer_key, username)
        
        http_requester = httplib2.Http()
        resp, content = http_requester.request(url, "GET")
        
        if resp['status'] == '200':
            json = simplejson.loads(content)
            
            # parse the request and check we have got back flickr id
            if json['stat'] == 'ok':
                
                userid = json['user']['id']
                  
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
            else:
                messages.error(request, 
    'Unable to validate your username with Flickr, please check your username and retry.')

        else:
            messages.error(request, 
    'Unable to validate your username with Flickr, please check your username and retry.')
           
    return redirect(settings_redirect(request))

@can_view_service
def stats(request, service_id):
    """Create up some stats."""
    
    service = get_object_or_404(UserService, pk=service_id)
    pictures = get_items(request.user, 
                         date.today() - timedelta(days=7), 
                         service)
    template_values = {}
    # most commented
    comments = 0
    template_values['most_commented_picture'] = None
    template_values['number_of_pictures_favorites'] = 0
    number_of_pictures_favorites = 0
    for pic in pictures:

        if pic.has_location():
            template_values['pic_centre'] = pic
        
        if pic.favorite:
            template_values['number_of_pictures_favorites'] = \
                           number_of_pictures_favorites + 1
        if int(pic.number_of_comments) > 0:
            if pic.number_of_comments > comments:
                comments = pic.number_of_comments
                template_values['most_commented_picture'] = pic
        
    template_values['pictures'] = pictures
    template_values['number_of_pictures_uploaded'] = len(pictures)
    
    if template_values['number_of_pictures_favorites'] == 0:
        template_values['number_of_pictures_favorites'] = "No favourite pictures this week."
        
    return render_to_response(
        service.template_name + '/stats.html',
        template_values,
        context_instance=RequestContext(request)
    )
