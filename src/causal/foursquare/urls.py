from django.conf.urls.defaults import *

base_path = r'^foursquare/'
shortcut = 'foursquare-urls'

urlpatterns = patterns('',
    url(r'^$', 'causal.foursquare.views.verify_auth', name='causal-foursquare'),
    url(r'^auth$', 'causal.foursquare.views.auth', name='causal-foursquare-auth'),
    url(r'^stats/(?P<service_id>\d+)$', 'causal.foursquare.views.stats', name='causal-foursquare-stats'),
)
