from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.importlib import import_module
from django.template.loader import render_to_string
from django.http import HttpResponseNotFound, HttpResponseServerError
from causal.main.decorators import cache_page

from causal.main.views import *

if settings.DEBUG:
    try:
        import causal.wingdbstub
    except ImportError:
        pass

from django.contrib import admin
admin.autodiscover()


cache_time = getattr(settings, 'ITEM_CACHE_TIME', 60 * 30)

urlpatterns = patterns('',
    url(r'^accounts/settings/$', user_settings, name='user-settings'),
    url(r'^accounts/settings/enable-service/(?P<app_id>\d+)$', enable_service, name='enable-service'),
    url(r'^accounts/settings/sharing/$', sharing_prefs, name='share-prefs'),

    url(r'^$', index, name='home'),
    url(r'^history/$', history, name='history'),
    url(r'^history/(?P<user_id>\d+)$', history, name='user-history'),
    url(r'^history/ajax/(?P<service_id>\d+)$', cache_page(history_callback, cache_time), name='history-callback'),
)

if getattr(settings, 'ENABLE_REGISTRATION', False):
    next_page = getattr(settings, 'LOGOUT_REDIRECT_URL', '/')
    urlpatterns += patterns('',
        url(
            r'^accounts/logout/$',
            'django.contrib.auth.views.logout',
            {'next_page': next_page,'template_name': 'registration/logout.html'}
        ),
        url(r'^accounts/', include('registration.urls')),
    )

if getattr(settings, 'ENABLE_ADMIN', False):
    urlpatterns += patterns('',
        url(settings.ADMIN_URL, include(admin.site.urls), name='admin'),
    )
if getattr(settings, 'ENABLE_ADMIN_DOCS', False):
    urlpatterns += patterns('',
        url(r'%sdoc/' % (settings.ADMIN_URL,), include('django.contrib.admindocs.urls')),
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
            'document_root': settings.MEDIA_ROOT }
         ),
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

