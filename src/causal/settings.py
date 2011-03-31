"""Django settings for causal project.
"""

import os

DEBUG = False
SERVE_STATIC = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Uncomment if you want to use a caching backend such as memcached to speed up
# certain views and actions
#CACHE_BACKEND = '' # e.g. 'memcached://127.0.0.1:11211'
#ITEM_CACHE_TIME = 60 * 30 # 30 mins, defaults to 30 mins if not set
ENABLE_CACHING = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

PATH_SITE_ROOT = os.path.normpath(os.path.dirname(__file__))

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PATH_SITE_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/_ca-media/'

# Whether or not to offload static requests to the Google CDN,
# e.g. for jQuery, jQueryUI etc.
USE_GOOGLE_CDN = False

# URLConf regex that defines the base dir for the admin URL.
# Should be set to something other than admin
ADMIN_URL = r'^_ca-admin/'

# Shiny admin panel or not?
ENABLE_ADMIN = False
ENABLE_ADMIN_DOCS = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = None

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'causal.main.middleware.messaging.AjaxMessaging',
    'causal.main.middleware.service_apps.SetupServiceApps',
)

ROOT_URLCONF = 'causal.urls'
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PATH_SITE_ROOT, 'main/templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.humanize',
    'south',
    'registration',
    'timezones',
    'causal.main',
)

INSTALLED_SERVICES = (
    #'causal.twitter',
    #'causal.foursquare',
    #'causal.flickr',
    #'causal.feed',
    #'causal.facebook',
    #'causal.github',
    #'causal.lastfm',
    #'causal.googlereader',
)

# SERVICE_CONFIG = {
#    'causal.twitter': {
#        'auth': {
#            'consumer_key': 'blah',
#            'consumer_secret': '123567890'
#        }
#    },
#    'causal.facebook': {
#        'auth': {
#            'consumer_key': 'blahblah',
#            'consumer_secret': '12356789012345'
#        }
#    },
#    'causal.foursquare': {
#        'auth': {
#            'consumer_key': 'ASDFGHJKLQWERTYUIOP',
#            'consumer_secret': 'ASDFGHJKL1234567890'
#        }
#    },
#    'causal.flickr': {
#        'auth': {
#            'api_key': 'asdfghjkl1234567890'
#        }
#    },
#    'causal.lastfm': {
#        'auth': {
#            'api_key': 'asdfghjkl1234567890'
#        }
#    }
# }

# Override INSTALLED_APPS_EXTEND or INSTALLED_SERVICES_EXTEND to add onto the default
# set of apps or services, rather than overriding them, in your
# local_settings.py
INSTALLED_APPS_EXTEND = list()
INSTALLED_SERVICES_EXTEND = list()

TEMPLATE_CONTEXT_PROCESSORS =(
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'causal.main.context_processors.registration.config',
)

# Account registration
ENABLE_REGISTRATION = False
ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# User profile model to provide extra data for Tiqual users
AUTH_PROFILE_MODULE = 'main.userprofile'

try:
    # Import local setting overrides, see local_settings.py.example
    from local_settings import *
except ImportError:
    pass

if ENABLE_ADMIN:
    INSTALLED_APPS += (
        'django.contrib.admin',
    )
if ENABLE_ADMIN_DOCS:
    INSTALLED_APPS += (
        'django.contrib.admindocs',
    )

if SECRET_KEY is None:
    raise Exception('SECRET_KEY needs to be changed to a unique, sekrit, random string')

TEMPLATE_DEBUG = DEBUG

if INSTALLED_SERVICES_EXTEND:
    INSTALLED_SERVICES += INSTALLED_SERVICES_EXTEND
if INSTALLED_APPS_EXTEND:
    INSTALLED_APPS += INSTALLED_APPS_EXTEND

INSTALLED_APPS += INSTALLED_SERVICES
