from time import mktime
from datetime import datetime, timedelta, date

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils import simplejson
from django.utils.html import urlize
from django.db.models import Count
from causal.main.forms import RegistrationForm
from causal.main.models import *
from causal.main.decorators import can_view_service

def history(request, user_id=None):
    template_values = {}

    if user_id:
        user = get_object_or_404(User, pk=user_id)
    else:
        if request.user.is_authenticated() and request.user.is_active:
            user = request.user
        else:
            return redirect('login')

    if request.user.is_authenticated()  and request.user.pk == user.pk:
        services = UserService.objects.filter(user=user, setup=True)
    else:
        services = UserService.objects.filter(user=user, setup=True, share=True)
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
        'index.html',
        template_values,
        context_instance=RequestContext(request)
    )

@can_view_service
def history_callback(request, service_id):
    template_values = {}
    service = get_object_or_404(UserService, pk=service_id)

    days = []
    days_to_i = {}
    day_one = date.today() - timedelta(days=7)
    today = date.today()

    for i in range(0,7):
        last = today - timedelta(days=i)
        days.append([])
        days_to_i[last.strftime('%A')] = i

    items = service.app.module.get_items(request.user, day_one, service)
    if items:
        for item in items:
            if item.created.date() > day_one:
                item_dict = {
                    'title': item.title,
                    'body': urlize(item.body),
                    'created': mktime(item.created.timetuple()),
                    'created_date': item.created.strftime("%I:%M%p").lower(),
                    'location': item.location,
                    'class_name' : item.class_name,
                    'has_location': item.has_location(),
                }
                days[days_to_i[item.created.strftime('%A')]].append(item_dict)

    response = {
        'class': service.class_name,
        'items': days,
    }
    return HttpResponse(simplejson.dumps(response))

def register(request):
    form = RegistrationForm()

    if request.user.is_authenticated():
        return redirect('/')

    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(form.cleaned_data['email'],
                form.cleaned_data['email'],
                form.cleaned_data['password1'])

            user = authenticate(username=form.cleaned_data['email'],
                                password=form.cleaned_data['password1'])
            login(request, user)

            return redirect('history')

    return render_to_response(
        'accounts/register.html',
        {
            'form' : form,
        },
        context_instance=RequestContext(request)
    )

@login_required(redirect_field_name='redirect_to')
def profile(request):
    """Edit access to various services"""
    available_services = ServiceApp.objects.all().exclude(userservice__user=request.user)
    return render_to_response(
        'accounts/profile.html',
        {
            'available_services': available_services,
        },
        context_instance=RequestContext(request)
    )

@login_required(redirect_field_name='redirect_to')
def enable_service(request, app_id):
    """Edit access to various services"""
    app = get_object_or_404(ServiceApp, pk=app_id)

    if not request.user.userservice_set.all().filter(app=app):
        service = UserService(user=request.user, app=app)
        request.user.userservice_set.add(service)
        request.user.save()
    return redirect('profile')

def index(request):
    users = User.objects.all().filter(is_active=True, userservice__share=True) \
        .annotate(service_count=Count('userservice')).filter(service_count__gt=0)
    return render_to_response(
        'homepage.html',
        {
            'users': users,
        },
        context_instance=RequestContext(request)
    )

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(redirect_field_name='redirect_to')
def sharing_prefs(request):
    """Enable/disable sharing preferences for services"""
    if request.method == 'POST':
        options = {}
        for k,v in request.POST.iteritems():
            if k.startswith('service_'):
                options[k] = bool(v)
            if ids:
                services = UserService.objects.filter(pk__in=options.keys(), user=request.user)
                for service in services:
                    service.share = options[service.pk]
                    service.save()
    if request.is_ajax():
        return HttpResponse(simplejson.dumps({'message': 'Saved'}))
    else:
        return redirect('profile')
