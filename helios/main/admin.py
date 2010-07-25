from main.models import OAuthAccessToken, OAuthRequestToken
from django.contrib import admin

class OAuthAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 
                    'oauth_token', 'oauth_token_secret',
                    'created')    
    
admin.site.register(OAuthAccessToken, OAuthAccessTokenAdmin)

class OAuthRequestTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 
                    'oauth_token', 'oauth_token_secret',
                    'created')

admin.site.register(OAuthRequestToken, OAuthRequestTokenAdmin)