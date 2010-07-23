from django.db import models
from django.contrib.auth.models import User

class OAuthRequestToken(models.Model):
    """OAuth Request Token."""

    user = models.ForeignKey(User)
    service = models.CharField(max_length=50)
    oauth_token = models.CharField(max_length=50)
    oauth_token_secret = models.CharField(max_length=50)
    created = models.DateTimeField()

class OAuthAccessToken(models.Model):
    """OAuth Access Token."""

    user = models.ForeignKey(User)
    service = models.CharField(max_length=50)
    specifier = models.CharField(max_length=50)
    oauth_token = models.CharField(max_length=50)
    oauth_token_secret = models.CharField(max_length=50)
    created = models.DateTimeField()