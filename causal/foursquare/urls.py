from django.conf.urls.defaults import *

base_path = r'^foursquare/'
shortcut = 'foursquare-urls'

urlpatterns = patterns('',
    url(r'^$', 'causal.foursquare.views.verify_auth', name='causal-foursquare-callback'),
    url(r'^auth$', 'causal.foursquare.views.auth', name='causal-foursquare-auth'),
)