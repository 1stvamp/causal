from django.conf.urls.defaults import *

base_path = r'^lastfm/'
shortcut = 'lastfm-urls'

urlpatterns = patterns('',
    url(r'^auth$', 'causal.lastfm.views.auth', name='causal-lastfm-auth'),
    url(r'^stats$', 'causal.lastfm.views.stats', name='causal-lastfm-stats'),
)
