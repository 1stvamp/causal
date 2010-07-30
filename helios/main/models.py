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
    oauth = models.ForeignKey(OAuthSetting)
    _module = None

    @property
    def module(self):
        if not self._module:
            self._module = import_module("%s.service" % (self.module_name,))
        return self._module

class UserService(models.Model):
    """User service handler. e.g. twitter, flickr etc."""

    user = models.ForeignKey(User)
    app = models.ForeignKey(ServiceApp)

class RequestToken(models.Model):
    """OAuth Request Token."""

    service = models.ForeignKey(UserService, null=True, blank=True)
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)
    created = models.DateTimeField()
    oauth_verify = models.CharField(max_length=255, blank=True, null=True)

class AccessToken(RequestToken):
    """OAuth Access Token."""
    pass

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
        return self.service.app_name.replace('.', '-')
