from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from models import OAuthAccessToken, OAuthRequestToken
from forms import RegistrationForm
import oauth2 as oauth
from settings import OAUTH_APP_SETTINGS
from django.utils import simplejson
@login_required(redirect_field_name='redirect_to')
def index(request):
    
    template_values = {}
    if request.method == 'GET':
        params = {
        'user' : request.user,
        'service' : 'twitter',
        }
    
        access_token_list = OAuthAccessToken.objects.filter(**params)
        if access_token_list:
            access_token = access_token_list[0]
            
            consumer = oauth.Consumer(OAUTH_APP_SETTINGS['twitter']['consumer_key'], 
                                      OAUTH_APP_SETTINGS['twitter']['consumer_secret'])
            token = oauth.Token(access_token.oauth_token , access_token.oauth_token_secret)
            
            client = oauth.Client(consumer, token)
            url = OAUTH_APP_SETTINGS['twitter']['default_api_prefix'] + '/statuses/user_timeline' + OAUTH_APP_SETTINGS['twitter']['default_api_suffix']
            resp, content = client.request(url, "GET")
            
            template_values['tweets'] = simplejson.loads(content)
            
        
        
    return render_to_response('index.html',template_values, 
        context_instance=RequestContext(request))

#@login_required(redirect_field_name='redirect_to')
def oauth_login(request, service=None):
    
    if request.method == 'GET':
        oauth_details = OAUTH_APP_SETTINGS[service]
        consumer = oauth.Consumer(OAUTH_APP_SETTINGS[service]['consumer_key'], 
                                  OAUTH_APP_SETTINGS[service]['consumer_secret'])
        
        client = oauth.Client(consumer)
        resp, content = client.request(oauth_details['request_token_url'], "GET")
        
        if resp['status'] != '200':
            print "fail"
            
        request_token_params = dict((token.split('=') for token in content.split('&')))
        
        token = OAuthRequestToken()
        token.service=service
        token.user = request.user
        token.oauth_token = request_token_params['oauth_token']
        token.oauth_token_secret = request_token_params['oauth_token_secret']
        token.created = datetime.now()
        token.save()
        
    return HttpResponseRedirect("%s?oauth_token=%s" % (oauth_details['user_auth_url'], 
                                         request_token_params['oauth_token']))

def oauth_callback(request, service=None):
    consumer = oauth.Consumer(OAUTH_APP_SETTINGS[service]['consumer_key'], 
                                  OAUTH_APP_SETTINGS[service]['consumer_secret'])
    
    params = {
        'oauth_token' : request.GET['oauth_token'],
        'service' : service,
        }
    
    request_token = OAuthRequestToken.objects.filter(**params)[0]
    
    token = oauth.Token(request_token.oauth_token, request_token.oauth_token_secret)
    client = oauth.Client(consumer, token)
    resp, content = client.request(OAUTH_APP_SETTINGS[service]['access_token_url'], "POST")

    access_token = dict((token.split('=') for token in content.split('&')))
    
    token_save = OAuthAccessToken()
    token_save.service=service
    token_save.user=request.user
    token_save.create=datetime.now()
    token_save.oauth_token=access_token['oauth_token']
    token_save.oauth_token_secret=access_token['oauth_token_secret']
                                                    
    token_save.save()
    
    return HttpResponseRedirect('/')
    
def register(request):
    form = RegistrationForm()
    
    if request.method == 'POST':
            
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(form.cleaned_data['username'], 
                                        form.cleaned_data['email'],
                                        form.cleaned_data['password1'])
            user = authenticate(username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password1'])
            login(request, user)
        
            return HttpResponseRedirect('/')
    
    return render_to_response('accounts/register.html',{
        'form' : form,
        }, 
        context_instance=RequestContext(request))
 
    
