from main.models import *
from django.contrib import admin

class AccessTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(AccessToken, AccessTokenAdmin)

class RequestTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(RequestToken, RequestTokenAdmin)

class ServiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Service, ServiceAdmin)

class OAuthSettingAdmin(admin.ModelAdmin):
    pass
admin.site.register(OAuthSetting, OAuthSettingAdmin)
