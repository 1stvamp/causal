from main.models import OAuthAccessToken, OAuthRequestToken, LastFMSettings, GitHubSettings
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

class LastFMSettingsAdmin(admin.ModelAdmin):
    list_display = ('username',)
    
admin.site.register(LastFMSettings, LastFMSettingsAdmin)