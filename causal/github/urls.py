from django.conf.urls.defaults import *

base_path = r'^github/'
shortcut = 'github-urls'

urlpatterns = patterns('',
        url(r'^auth$', 'causal.github.views.auth', name='causal-github-auth'),
)
