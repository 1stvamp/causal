from django.conf.urls.defaults import *

base_path = r'^tumblr/'
shortcut = 'tumblr-urls'

urlpatterns = patterns('',
    url(r'^auth$', 'causal.tumblr.views.auth', name='causal-tumblr-auth'),
    url(r'^stats/(?P<service_id>\d+)$', 'causal.tumblr.views.stats', name='causal-tumblr-stats'),
)
