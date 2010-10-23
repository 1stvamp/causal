from django.conf.urls.defaults import *

base_path = r'^twitter/'
shortcut = 'twitter-urls'

urlpatterns = patterns('',
    url(r'^$', 'causal.twitter.views.verify_auth', name='causal-twitter-callback'),
    url(r'^auth$', 'causal.twitter.views.auth', name='causal-twitter-auth'),
    url(r'^stats/(?P<service_id>\d+)$', 'causal.twitter.views.stats', name='causal-twitter-stats'),
)
