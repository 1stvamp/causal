from time import mktime
from datetime import datetime, timedelta, date

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils import simplejson
from django.utils.html import urlize
from django.db.models import Count
from causal.main.models import *
from causal.main.decorators import can_view_service
from causal.main.exceptions import ServiceError
from causal.main.forms import UserProfileForm
from django.contrib import messages

def history(request, username):
    template_values = {}

    user = get_object_or_404(User, username=username)
    template_values['viewing_user'] = user

    filters = {
        'user': user,
        'setup': True,
    }
    if not request.user.is_authenticated() or not request.user.pk == user.pk:
        filters['share'] = True

    services = UserService.objects.filter(**filters).order_by('app__module_name')
    template_values['services'] = services

    days = []
    day_names = {}
    days_to_i = {}
    day_one = date.today() - timedelta(days=7)
    today = date.today()

    for i in range(0,7):
        last = today - timedelta(days=i)
        days.append([])
        day_names[i] = last.strftime('%A')
        days_to_i[day_names[i]] = i

    template_values['days'] = days
    template_values['day_names'] = day_names

    return render_to_response(
        'causal/history.html',
        template_values,
        context_instance=RequestContext(request)
    )

@can_view_service
def history_callback(request, username, service_id):
    template_values = {}
    service = get_object_or_404(UserService, pk=service_id, user__username=username)

    days = []
    days_to_i = {}
    day_one = date.today() - timedelta(days=7)
    today = date.today()

    for i in range(0,7):
        last = today - timedelta(days=i)
        days.append([])
        days_to_i[last.strftime('%A')] = i

    response = {
        'class': service.class_name,
        'error': False,
        'items': [],
    }
    try:
        items = service.app.module.get_items(request.user, day_one, service)
        if items:
            for item in items:
                if item.created_local.date() > day_one:
                    item_dict = {
                        'title': item.title,
                        'body': urlize(item.body),
                        'created': mktime(item.created_local.timetuple()),
                        'created_date': item.created_local.strftime("%I:%M%p").lower(),
                        'location': item.location,
                        'class_name' : item.class_name,
                        'has_location': item.has_location(),
                        'link_back' : item.link_back,
                    }
                    days[days_to_i[item.created_local.strftime('%A')]].append(item_dict)
            response['items'] = days
    except ServiceError:
        response['error'] = True

    return HttpResponse(simplejson.dumps(response))

@login_required(redirect_field_name='redirect_to')
def user_settings(request):
    """Edit access to various services"""
    
    # services available to user
    available_services = ServiceApp.objects.all().exclude(userservice__user=request.user)
    
    # services yet to be setup
    available_services_unconfigured = UserService.objects.all().filter(user=request.user, setup=False)
    
    # services setup and running
    enabled_services = UserService.objects.all().filter(user=request.user, setup=True)
    
    if request.method == 'POST':
        if request.POST.get('user', None) != str(request.user.id):
            return HttpResponseNotAllowed('Not your user!')
        form = UserProfileForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'This is a success message.')
            return redirect('user-settings')
    else:
        form = UserProfileForm(instance=request.user.get_profile())
    return render_to_response(
        'causal/users/settings.html',
        {
            'enabled_services' : enabled_services,
            'available_services': available_services,
            'available_services_unconfigured' : available_services_unconfigured,
            'form': form,
        },
        context_instance=RequestContext(request)
    )

@login_required(redirect_field_name='redirect_to')
def enable_service(request, app_id):
    """Edit access to various services"""
    app = get_object_or_404(ServiceApp, pk=app_id)
    
    # setup oauth based service
    if hasattr(app.module, 'enable'):
        return app.module.enable()
    
    # setup username services
    if not request.user.userservice_set.all().filter(app=app):
        service = UserService(user=request.user, app=app)
        request.user.userservice_set.add(service)
        request.user.save()
    
    return redirect('user-settings')

def index(request):
    """Displays user listing of sharing users or redirects to setting page
    if user has no configured services."""

    # check if user has available services and they are logged in
    # if so send them to the profile page to get setup
    if request.user.is_authenticated():
        services = UserService.objects.all().filter(user=request.user)
        if not services:
            return redirect(reverse('user-settings'))
        return redirect('/%s/' % request.user.username)
    
    users = User.objects.all().filter(is_active=True, userservice__share=True, userservice__setup=True) \
        .annotate(service_count=Count('userservice')).filter(service_count__gt=0)
        
    return render_to_response(
        'causal/userlist.html',
        {
            'users': users,
        },
        context_instance=RequestContext(request)
    )

@login_required(redirect_field_name='redirect_to')
def sharing_prefs(request):
    """Enable/disable sharing preferences for services"""
    if request.method == 'POST':
        options = {}
        for k,v in request.POST.iteritems():
            if k.startswith('service_'):
                if v == 'on':
                    v = True
                elif v == 'off':
                    v = False
                else:
                    v = bool(v)
                options[int(k.replace('service_', ''))] = v
        services = UserService.objects.filter(user=request.user)
        for service in services:
            service.share = options.get(service.pk, False)
            service.save()
    if request.is_ajax():
        return HttpResponse(simplejson.dumps({'message': 'Saved'}))
    else:
        return redirect('user-settings')

def userfeed(request, username):
    user = get_object_or_404(User, username=username)

    filters = {
        'user': user,
        'setup': True,
    }
    if not request.user.is_authenticated() or not request.user.pk == user.pk:
        filters['share'] = True

    services = UserService.objects.filter(**filters).order_by('app__module_name')
    
    data = []
    for service in services:
        data = data + service.app.module.get_items_as_json(request.user, date.today() - timedelta(days=7), service)
    
    return HttpResponse(simplejson.dumps({'results': data}))
