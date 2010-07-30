from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module


class OAuthSetting(models.Model):
    """OAuth App Settings."""

    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    request_token_url = models.URLField()
    access_token_url = models.URLField()
    user_auth_url = models.URLField()
    default_api_prefix = models.CharField(max_length=50)
    default_api_suffix = models.CharField(max_length=50)
    created = models.DateTimeField()

class Service(models.Model):
    """User service handler. e.g. twitter, flickr etc."""

    name = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    oauth = models.ForeignKey(OAuthSetting)
    app_name = models.CharField(max_length=255)
    _app = None

    @property
    def app(self):
        if not self._app:
            self._app = import_module(self.app_name)
        return self._app

class RequestToken(models.Model):
    """OAuth Request Token."""

    service = models.ForeignKey(Service, null=True, blank=True)
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)
    created = models.DateTimeField()

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
