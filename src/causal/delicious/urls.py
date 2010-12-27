from django.conf.urls.defaults import *

base_path = r'^delicious/'
shortcut = 'delicious-urls'

urlpatterns = patterns('',
    url(r'^auth$', 'causal.delicious.views.auth', name='causal-delicious-auth'),
    url(r'^stats/(?P<service_id>\d+)$', 'causal.delicious.views.stats', name='causal-delicious-stats'),
)
