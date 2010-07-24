from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^helios/', include('helios.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^oauth/', include(admin.site.urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/', include(admin.site.urls)),
    url(r'^oauth/(?P<service>\w+)/login/$', 'main.views.oauth_login', name='oauth_login'),
    url(r'^oauth/(?P<service>\w+)/callback/$', 'main.views.oauth_callback', name='oauth_callback'),
    
    #users
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^accounts/register/$', 'main.views.register', name='register'),
    (r'^password_reset/$',     'django.contrib.auth.views.password_reset'),
    (r'^password_reset/done/$','django.contrib.auth.views.password_reset_done'),
    url(r'^$', 'main.views.index', name='index'),
)
