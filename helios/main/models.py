from django.db import models
from django.contrib.auth.models import User

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
    name = models.CharField(max_length=50)
    oauth = models.ForeignKey(OAuthSetting)
    app = models.CharField(max_length=255)

class OAuthRequestToken(models.Model):
    """OAuth Request Token."""

    user = models.ForeignKey(User)
    service = models.ForeignKey(Service)
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)
    created = models.DateTimeField()

class OAuthAccessToken(OAuthRequestToken):
    """OAuth Access Token."""
    pass