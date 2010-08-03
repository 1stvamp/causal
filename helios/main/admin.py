from helios.main.models import *
from django.contrib import admin

class AccessTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(AccessToken, AccessTokenAdmin)

class RequestTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(RequestToken, RequestTokenAdmin)

class UserServiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserService, UserServiceAdmin)

class ServiceAppAdmin(admin.ModelAdmin):
    pass
admin.site.register(ServiceApp, ServiceAppAdmin)

class OAuthSettingAdmin(admin.ModelAdmin):
    pass
admin.site.register(OAuthSetting, OAuthSettingAdmin)
