from django.conf.urls.defaults import *

base_path = r'^foursquare/'
shortcut = 'foursquare-urls'

urlpatterns = patterns('',
    url(r'^$', 'helios.foursquare.views.verify_auth', name='helios-foursquare-callback'),
    url(r'^auth$', 'helios.foursquare.views.auth', name='helios-foursquare-auth'),
)
