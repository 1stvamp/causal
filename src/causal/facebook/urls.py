from django.conf.urls.defaults import *

base_path = r'^facebook/'
shortcut = 'facebook-urls'

urlpatterns = patterns('',
    url(r'^$', 'causal.facebook.views.verify_auth', name='causal-facebook-callback'),
    url(r'^auth$', 'causal.facebook.views.auth', name='causal-facebook-auth'),
    url(r'^stats/(?P<service_id>\d+)$', 'causal.facebook.views.stats', name='causal-facebook-stats'),
)
