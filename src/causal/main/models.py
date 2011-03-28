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
    module_name = models.CharField(max_length=255, db_index=True)
    enable = models.NullBooleanField(null=True, blank=True, default=True)
    _module = None

    @property
    def module(self):
        if not self._module:
            self._module = import_module("%s.service" % (self.module_name,))
        return self._module
    
    @property
    def display_name(self):
        return self.module.ServiceHandler.display_name

    def __unicode__(self):
        return u'%s service app' % (self.module.ServiceHandler.display_name,)

    @property
    def auth_settings(self):
        """App specific auth settings from the settings module
        """
        app_settings = getattr(settings, 'SERVICE_CONFIG', {}).get(
            self.module_name, {}).get('auth', None)
        if app_settings:
            return app_settings
        else:
            raise Exception(
                'Missing "auth" in settings.SERVICES_CONFIG for %s' % \
                    (self.module_name,)
            )

def get_app_by_name(module_name):
    """Shortcut function to return the correct service app
    """

    app = ServiceApp.objects.get_or_create(module_name=module_name)[0]
    return app

class UserService(models.Model):
    """User service handler. e.g. twitter, flickr etc.
    """

    user = models.ForeignKey(User, db_index=True)
    app = models.ForeignKey(ServiceApp, db_index=True)
    setup = models.NullBooleanField(null=True, blank=True, default=False)
    share = models.NullBooleanField(null=True, blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # Used to identify if the remote service is publically available i.e. twitter
    public = models.NullBooleanField(null=True, blank=True, default=False)

    auth_type = models.ForeignKey(ContentType, blank=True, null=True)
    auth_object_id = models.PositiveIntegerField(blank=True, null=True)
    auth = generic.GenericForeignKey('auth_type', 'auth_object_id')

    _handler = None
    
    class Meta:
        unique_together = ("user", "app",)

    @property
    def form_template_path(self):
        if self.handler.custom_form:
            path = "%s/form.html" % (self.template_name,)
        elif self.handler.oauth_form:
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
        """Return a handler class specific to the calling service.
        """
        if self._handler:
            return self._handler
        else:
            # Fetch class for service, and inject this model instance
            self._handler = self.app.module.ServiceHandler(self)
            return self._handler

class BaseAuth(models.Model):
    """Base authentication class for identifying against a service.
    """

    user_services = generic.GenericRelation(
        UserService,
        content_type_field='auth_type',
        object_id_field='auth_object_id'
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class Auth(BaseAuth):
    """Auth for sites requiring a username.
    """

    username = models.CharField(max_length=255)
    secret = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        if self.user_services.count() > 0:
            return u'Auth tokens for %s' % (self.user_services.all()[0],)
        else:
            return u'Auth tokens'

class RequestToken(models.Model):
    """OAuth Request Token.
    """

    oauth_token = models.CharField(max_length=255, blank=True, null=True)
    oauth_token_secret = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    oauth_verify = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        if self.oauth_set.count() > 0 and \
          self.oauth_set.all()[0].user_services.count() > 0:
            return u'Request token for %s' % (self.oauth_set.all()[0].user_services.all()[0],)
        else:
            return u'Request token'

class AccessToken(RequestToken):
    """OAuth Access Token.
    """

    def __unicode__(self):
        if self.oauth_set.count() > 0 and \
          self.oauth_set.all()[0].user_services.count() > 0:
            return u'Access token for %s' % (self.oauth_set.all()[0].user_services.all()[0],)
        else:
            return u'Access token'

class OAuth(BaseAuth):
    """Auth details for sites requiring OAuth permission.
    """

    request_token = models.ForeignKey(RequestToken, null=True, blank=True)
    access_token = models.ForeignKey(AccessToken, related_name="%(app_label)s_%(class)s_related", null=True, blank=True)

    def __unicode__(self):
        if self.user_services.count():
            return u'OAuth tokens for %s' % (self.user_services.all()[0],)
        else:
            return u'OAuth tokens'

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
    def __init__(self):
        self.created = None #datetime
        self.title = None #str/unicode
        self.body = None #str/unicode
        self.location = {
            'long': None, #str
            'lat': None, #str
        } #dict
        self.service = None #Service
        self.link_back = None #str/unicode

    @property
    def class_name(self):
        return self.service and self.service.class_name or ''

    def has_location(self):
        return self.location.has_key('long') is not False \
            and self.location.has_key('lat') is not False

    @property
    def created_local(self):
        if hasattr(self.service.user, 'get_profile'):
            return adjust_datetime_to_timezone(
                self.created,
                'UTC',
                unicode(self.service.user.get_profile().timezone)
            )
        else:
            return adjust_datetime_to_timezone(self.created, 'UTC', TIME_ZONE)
