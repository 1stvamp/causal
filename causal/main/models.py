from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.core.urlresolvers import reverse


class OAuthSetting(models.Model):
    """OAuth App Settings."""

    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    request_token_url = models.URLField(verify_exists=False)
    access_token_url = models.URLField(verify_exists=False)
    user_auth_url = models.URLField(verify_exists=False)
    created = models.DateTimeField()
    callback_url_base = models.CharField(max_length=255)

    def __unicode__(self):
        url = self.request_token_url
        return u'OAuth (%s%s)' % (url[:19], len(url) > 20 and '...' or '')

class ServiceApp(models.Model):
    module_name = models.CharField(max_length=255)
    oauth = models.ForeignKey(OAuthSetting, blank=True, null=True)
    _module = None

    @property
    def module(self):
        if not self._module:
            self._module = import_module("%s.service" % (self.module_name,))
        return self._module

    def __unicode__(self):
        return u'%s service app' % (self.module.DISPLAY_NAME,)

class UserService(models.Model):
    """User service handler. e.g. twitter, flickr etc."""

    user = models.ForeignKey(User)
    app = models.ForeignKey(ServiceApp)
    setup = models.NullBooleanField(null=True, blank=True, default=False)
    share = models.NullBooleanField(null=True, blank=True, default=True)

    @property
    def form_template_path(self):
        if self.app.module.CUSTOM_FORM:
            path = "%s/form.html" % (self.app.module_name,)
        elif self.app.module.OAUTH_FORM:
            path = "services/oauth_form.html"
        else:
            path = "services/username_form.html"
        return path

    def __unicode__(self):
        return u'%s service for %s' % (self.app, self.user,)

    def get_auth_url(self):
        return reverse('%s-auth' % (self.app.module_name.replace('.', '-'),))

    @property
    def class_name(self):
        return self.app.module_name.replace('.', '-')

class RequestToken(models.Model):
    """OAuth Request Token."""

    service = models.ForeignKey(UserService, null=True, blank=True)
    oauth_token = models.CharField(max_length=255, blank=True, null=True)
    oauth_token_secret = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField()
    oauth_verify = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u'%s request token for %s' % (self.service.app.module.DISPLAY_NAME, self.service.user,)

class AccessToken(RequestToken):
    """OAuth Access Token."""

    # For services such as Github et al that use user/API key auth
    username = models.CharField(max_length=255, blank=True, null=True)
    api_token = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u'%s access token for %s' % (self.service.app.module.DISPLAY_NAME, self.service.user,)

# Not a django.db.models.Model, just a common container for service data

class ServiceItem(object):
    created = None #datetime
    title = None #str/unicode
    body = None #str/unicode
    location = {
        'long': None, #str
        'lat': None, #str
    } #dict
    service = None #Service
    link_back = None #str/unicode

    @property
    def class_name(self):
        return self.service and self.service.app.module_name.replace('.', '-') or ''

    def has_location(self):
        return self.location.has_key('long') is not False and self.location.has_key('lat') is not False
