from datetime import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app
from django.db.models.signals import post_save, post_syncdb
from django.utils.importlib import import_module
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from timezones.fields import TimeZoneField, MAX_TIMEZONE_LENGTH
from timezones.utils import adjust_datetime_to_timezone

User = auth_app.User

# Prevent interactive question about wanting a superuser created.
post_syncdb.disconnect(
    create_superuser,
    sender=auth_app,
    dispatch_uid = "django.contrib.auth.management.create_superuser"
)

TIME_ZONE = getattr(settings, 'TIME_ZONE', 'Europe/London')


class ServiceApp(models.Model):
    module_name = models.CharField(max_length=255)
    _module = None

    @property
    def module(self):
        if not self._module:
            self._module = import_module("%s.service" % (self.module_name,))
        return self._module

    def __unicode__(self):
        return u'%s service app' % (self.module.DISPLAY_NAME,)
def get_app(module_name):
    """Shortcut function to return the correct service app
    """
    app = ServiceApp.objects.get_or_create(module_name=module_name)
    return app

class UserService(models.Model):
    """User service handler. e.g. twitter, flickr etc."""

    user = models.ForeignKey(User)
    app = models.ForeignKey(ServiceApp)
    setup = models.NullBooleanField(null=True, blank=True, default=False)
    share = models.NullBooleanField(null=True, blank=True, default=False)

    # Used to identify if the remote service is publically available i.e. twitter
    public = models.NullBooleanField(null=True, blank=True, default=False)

    auth_type = models.ForeignKey(ContentType, blank=True, null=True)
    auth_object_id = models.PositiveIntegerField(blank=True, null=True)
    auth = generic.GenericForeignKey('auth_type', 'auth_object_id')

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
        return self.app.module_name.replace('.', '-')

    @property
    def template_name(self):
        return self.app.module_name.replace('.', '/')

    @property
    def handler(self):
        """Return a handler class specific to the calling service."""
        if hasattr(self, '_handler'):
            return self._handler
        else:
            # fetch the class from our service
            self._handler = self.app.module.ServiceHandler(self.user_id)
            return self._handler

class BaseAuth(models.Model):
    """Base authentication class for identifying against a service"""

    user_services = generic.GenericRelation(
        UserService,
        content_type_field='auth_type_fk',
        object_id_field='auth_object_id'
    )
    created = models.DateTimeField()
    modified = models.DateTimeField()

class Auth(BaseAuth):
    """Auth for sites requiring a username."""

    username = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)

    def __unicode__(self):
        if hasattr(self, 'userservice_set'):
            return u'Auth for %s' % (self.userservice_set[0],)
        else:
            return u'Auth settings'

class RequestToken(models.Model):
    """OAuth Request Token."""

    oauth_token = models.CharField(max_length=255, blank=True, null=True)
    oauth_token_secret = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField()
    oauth_verify = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u'%s request token for %s' % (self.service.app.module.DISPLAY_NAME, self.service.user,)

class AccessToken(RequestToken):
    """OAuth Access Token."""

    def __unicode__(self):
        return u'%s access token for %s' % (self.service.app.module.DISPLAY_NAME, self.service.user,)

class OAuth(BaseAuth):
    """Auth details for sites requiring OAuth permission"""

    request_token = models.ForeignKey(RequestToken, null=True, blank=True)
    access_token = models.ForeignKey(AccessToken, related_name="%(app_label)s_%(class)s_related", null=True, blank=True)

    def __unicode__(self):
        if self.userservice_set:
            return u'OAuth for %s' % (self.userservice_set[0],)
        else:
            return u'OAuth settings'

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
        up = UserProfile()
        up.user = kwargs['instance']
        # *sigh*, because certain ppl haven't pushed a new release for Django 1.2,
        # we'll have to monkey patch this for now
        up._meta.fields[-1].to_python = lambda x: unicode(x)
        up.timezone = TIME_ZONE
        up.save()
post_save.connect(user_save_handler, User)

# Allow South to handle TimeZoneField smoothly
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        rules=[(
            (TimeZoneField,),
            [],
            { "max_length": ["max_length", { "default": MAX_TIMEZONE_LENGTH }],}
        )],
        patterns=['timezones\.fields\.']
    )
except ImportError:
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
    link_back = None #str/unicode
    user = None #auth.user instance

    @property
    def class_name(self):
        return self.service and self.service.app.module_name.replace('.', '-') or ''

    def has_location(self):
        return self.location.has_key('long') is not False and self.location.has_key('lat') is not False

    @property
    def created_local(self):
        if hasattr(self.user, 'get_profile'):
            return adjust_datetime_to_timezone(self.created, 'UTC', unicode(self.user.get_profile().timezone))
        else:
            return adjust_datetime_to_timezone(self.created, 'UTC', TIME_ZONE)
