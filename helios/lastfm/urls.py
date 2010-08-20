from django.conf.urls.defaults import *

base_path = r'^lastfm/'
shortcut = 'lastfm-urls'

urlpatterns = patterns(
    url(r'^auth$', 'helios.lastfm.views.auth', name='helios-lastfm-auth'),
)
