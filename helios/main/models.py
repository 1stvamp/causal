from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module


class OAuthSetting(models.Model):
    """OAuth App Settings."""

    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    request_token_url = models.URLField(verify_exists=False)
    access_token_url = models.URLField(verify_exists=False)
    user_auth_url = models.URLField(verify_exists=False)
    created = models.DateTimeField()
    callback_url_base = models.CharField(max_length=255)

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
        return u'%s service app' % (self.module.display_name,)

class UserService(models.Model):
    """User service handler. e.g. twitter, flickr etc."""

    user = models.ForeignKey(User)
    app = models.ForeignKey(ServiceApp)

    @property
    def form_template_path(self):
        return "%s/form.html" % (self.app.module_name,)

    def __unicode__(self):
        return u'%s service for %s' % (self.app, self.user,)

class RequestToken(models.Model):
    """OAuth Request Token."""

    service = models.ForeignKey(UserService, null=True, blank=True)
    oauth_token = models.CharField(max_length=255, blank=True, null=True)
    oauth_token_secret = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField()
    oauth_verify = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u'%s request token for %s' % (self.service.app.module.display_name, self.service.user,)

class AccessToken(RequestToken):
    """OAuth Access Token."""

    # For services such as Github et al that use user/API key auth
    username = models.CharField(max_length=255, blank=True, null=True)
    api_token = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u'%s access token for %s' % (self.service.app.module.display_name, self.service.user,)

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

    @property
    def class_name(self):
        return self.service.app.module_name.replace('.', '-')

    def has_location(self):
        return self.location['long'] is not None and self.location['lat'] is not None
