from datetime import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app
from django.db.models.signals import post_save, post_syncdb
from django.utils.importlib import import_module
from django.core.urlresolvers import reverse
from timezones.fields import TimeZoneField, MAX_TIMEZONE_LENGTH
from timezones.utils import adjust_datetime_to_timezone

User = auth_app.User

# Prevent interactive question about wanting a superuser created.  (This
# code has to go in this otherwise empty "models" module so that it gets
# processed by the "syncdb" command during database creation.)
post_syncdb.disconnect(
    create_superuser,
    sender=auth_app,
    dispatch_uid = "django.contrib.auth.management.create_superuser"
)

TIME_ZONE = getattr(settings, 'TIME_ZONE', 'Europe/London')

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
    share = models.NullBooleanField(null=True, blank=True, default=False)
    
    # used to identify if the remote service is publically available i.e. twitter
    public = models.NullBooleanField(null=True, blank=True, default=False)

    @property
    def form_template_path(self):
        if self.app.module.CUSTOM_FORM:
            path = "%s/form.html" % (self.template_name,)
        elif self.app.module.OAUTH_FORM:
            path = "causal/services/oauth_form.html"
        else:
            path = "causal/services/username_form.html"
        return path

    def __unicode__(self):
        return u'%s service for %s' % (self.app, self.user,)

    def get_auth_url(self):
        return reverse('%s-auth' % (self.app.module_name.replace('.', '-'),))

    @property
    def class_name(self):
        """Return the name for the html class used in templates"""
        return self.app.module_name.replace('.', '-')
    
    @property
    def template_name(self):
        return self.app.module_name.replace('.', '/')

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
    userid = models.CharField(max_length=255, blank=True, null=True)
    api_token = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u'%s access token for %s' % (self.service.app.module.DISPLAY_NAME, self.service.user,)

class UserProfile(models.Model):
    """Model for providing extra information for a user, can be
    accessed via the User.get_profile() method.
    """
    user = models.ForeignKey(User)
    timezone = TimeZoneField()

def user_save_handler(sender, **kwargs):
    # Make sure we create a matching UserProfile instance whenever
    # a new User is created.
    if kwargs['created']:
        # Check for existing profile, possible if loaded from a fixture
        try:
            kwargs['instance'].get_profile()
        except UserProfile.DoesNotExist:
            up = UserProfile()
            up.user = kwargs['instance']
            up.save()
post_save.connect(user_save_handler, User)


# Not a django.db.models.Model, just a common container for service data

class ServiceItem(object):
    """Our customer model for storing a normalised model of a feed item
    from a third party."""
    
    created = None #datetime
    title = None #str/unicode
    body = None #str/unicode
    location = {
        'long': None, #str
        'lat': None, #str
    } #dict
    service = None #Service
    link_back = None #str/unicode
    user = None #auth.user instance

    @property
    def class_name(self):
        """Return the name for the html class used in templates"""
        return self.service and self.service.app.module_name.replace('.', '-') or ''

    def has_location(self):
        return self.location.has_key('long') is not False and self.location.has_key('lat') is not False

    @property
    def created_local(self):
        """Calculate the created time using timexone to give a datetime
        in the users time zone."""
        if hasattr(self, 'created'):
            if hasattr(self.user, 'get_profile'):
                return adjust_datetime_to_timezone(self.created, 'UTC', unicode(self.user.get_profile().timezone))
            else:
                return adjust_datetime_to_timezone(self.created, 'UTC', TIME_ZONE)
        else:
            return None
