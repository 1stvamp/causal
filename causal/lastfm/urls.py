from django.conf.urls.defaults import *

base_path = r'^lastfm/'
shortcut = 'lastfm-urls'

urlpatterns = patterns('',
    url(r'^auth$', 'causal.lastfm.views.auth', name='causal-lastfm-auth'),
)
