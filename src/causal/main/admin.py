from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.importlib import import_module
from causal.main.models import *

class AccessTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(AccessToken, AccessTokenAdmin)

class RequestTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(RequestToken, RequestTokenAdmin)

class UserServiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserService, UserServiceAdmin)

# Add a custom form to the ServiceApp admin so we can present
# choices in the module_name field matching INSTALLED_SERVICES

SERVICES_CHOICES = []
for service_name in settings.INSTALLED_SERVICES:
    service = import_module("%s.service" % (service_name,))
    if service:
        SERVICES_CHOICES.append((service_name,
            service.ServiceHandler.display_name,))

class ServiceAppAdminForm(forms.ModelForm):
    module_name = forms.ChoiceField(choices=SERVICES_CHOICES, label='Application')

class ServiceAppAdmin(admin.ModelAdmin):
    form = ServiceAppAdminForm
admin.site.register(ServiceApp, ServiceAppAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)

class AuthAdmin(admin.ModelAdmin):
    pass
admin.site.register(Auth, AuthAdmin)

class OAuthAdmin(admin.ModelAdmin):
    pass
admin.site.register(OAuth, OAuthAdmin)

