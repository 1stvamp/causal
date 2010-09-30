from django.conf.urls.defaults import *

base_path = r'^flickr/'
shortcut = 'flickr-urls'

urlpatterns = patterns('',
    url(r'^auth$', 'causal.flickr.views.auth', name='causal-flickr-auth'),
)
