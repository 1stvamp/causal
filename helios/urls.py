from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.importlib import import_module
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

if settings.DEBUG:
    try:
        import helios.wingdbstub
    except ImportError:
        pass

urlpatterns = patterns('',
    # Example:
    # (r'^helios/', include('helios.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^oauth/', include(admin.site.urls), name='oath'),

    #users
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^accounts/register/$', 'main.views.register', name='register'),
    url(r'^accounts/profile/$', 'main.views.profile', name='register'),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password-reset'),
    url(r'^password_reset/done/$','django.contrib.auth.views.password_reset_done', name='post-password-reset'),
    url(r'^$', 'main.views.register', name='register'),
    url(r'^history/$', 'main.views.history', name='history'),
)

for service_name in settings.INSTALLED_SERVICES:
    service_urls = import_module("%s.urls" % (service_name,))
    if service_urls:
	urlpatterns += patterns('',
	    url(service_urls.base_path, include(service_urls), name=service_urls.shortcut),
	)

if settings.SERVE_STATIC:
	urlpatterns += patterns('',
	    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
	    	'document_root': settings.MEDIA_ROOT }),
	)