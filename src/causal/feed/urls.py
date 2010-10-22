from django.conf.urls.defaults import *

base_path = r'^feed/'
shortcut = 'feed-urls'

urlpatterns = patterns('',
    url(r'^stats/(?P<service_id>\d+)$', 'causal.feed.views.stats', name='causal-feed-stats'),

)
