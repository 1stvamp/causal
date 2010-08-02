from django.conf.urls.defaults import *

base_path = r'^twitter/'
shortcut = 'twitter-urls'

urlpatterns = patterns('',
    url(r'^$', 'helios.twitter.views.verify_auth', name='helios-twitter-callback'),
    url(r'^auth$', 'helios.twitter.views.auth', name='helios-twitter-auth'),
)