from django.conf.urls.defaults import *

base_path = r'^flickr/'
shortcut = 'flickr-urls'

urlpatterns = patterns('',
    url(r'^auth$', 'helios.flickr.views.auth', name='helios-flickr-auth'),
)
