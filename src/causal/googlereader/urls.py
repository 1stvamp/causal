from django.conf.urls.defaults import *

base_path = r'^googlereader/'
shortcut = 'googlereader-urls'

urlpatterns = patterns('',
        url(r'^auth$', 'causal.googlereader.views.auth', name='causal-googlereader-auth'),
        url(r'^stats/(?P<service_id>\d+)$', 'causal.googlereader.views.stats', name='causal-googlereader-stats'),
)
