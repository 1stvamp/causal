from django.conf.urls.defaults import *

base_path = r'^github/'
shortcut = 'github-urls'

urlpatterns = patterns('',
        url(r'^auth$', 'helios.github.views.auth', name='helios-github-auth'),
)
