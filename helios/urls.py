from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.importlib import import_module
from django.template.loader import render_to_string
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
    url(r'^accounts/register/$', 'helios.main.views.register', name='register'),
    url(r'^accounts/profile/$', 'helios.main.views.profile', name='profile'),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password-reset'),
    url(r'^password_reset/done/$','django.contrib.auth.views.password_reset_done', name='post-password-reset'),
    url(r'^$', 'helios.main.views.register', name='register'),
    url(r'^history/$', 'helios.main.views.history', name='history'),
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

# These custom error handlers return the correct Http codes for their respective
# errors, as opposed to a 200 as normally returned.
# We can also redirect to templates wherever we like here.
handler404 = '%s.return_404' % (settings.ROOT_URLCONF,)
handler500 = '%s.return_500' % (settings.ROOT_URLCONF,)

def return_404(request):
	return HttpResponseNotFound(render_to_string("404.html"))

def return_500(request):
	return HttpResponseServerError(render_to_string("500.html"))

