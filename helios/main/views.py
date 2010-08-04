from datetime import datetime, timedelta, date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.template import RequestContext

from helios.main.forms import RegistrationForm
from helios.main.models import *

@login_required(redirect_field_name='redirect_to')
def history(request, user_id=None):
    template_values = {}
    if user_id:
        user = get_object_or_404(User, pk=user_id)
    else:
        if request.user.is_authenticated() and request.user.is_active:
            user = request.user
        else:
            return redirect('register')

    services = UserService.objects.filter(user=request.user)
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

    for service in services:
        items = service.app.module.get_items(request.user, day_one, service)
        if items:
            for item in items:
                if item.created.date() > day_one:
                    days[days_to_i[item.created.strftime('%A')]].append(item)

    if days:
        for day in days:
            day.sort(key=lambda item:item.created, reverse=True)

    template_values['days'] = days
    template_values['day_names'] = day_names

    return render_to_response(
        'index.html',
        template_values,
        context_instance=RequestContext(request)
    )

def register(request):
    form = RegistrationForm()

    if request.user.is_authenticated():
        return redirect('history')

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
    return render_to_response(
        'accounts/profile.html',
        {
        },
        context_instance=RequestContext(request)
    )
