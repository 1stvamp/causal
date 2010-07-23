from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from models import OAuthAccessToken, OAuthRequestToken
from forms import RegistrationForm

@login_required(redirect_field_name='redirect_to')
def index(request):
    
    if request.method == 'GET':
        pass
        
    return render_to_response('index.html',{}, 
        context_instance=RequestContext(request))

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
 
    
