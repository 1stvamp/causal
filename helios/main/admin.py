from main.models import *
from django.contrib import admin

class OAuthAccessTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(OAuthAccessToken, OAuthAccessTokenAdmin)

class OAuthRequestTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(OAuthRequestToken, OAuthRequestTokenAdmin)

class ServiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Service, ServiceAdmin)

class OAuthSettingAdmin(admin.ModelAdmin):
    pass
admin.site.register(OAuthSetting, OAuthSettingAdmin)
