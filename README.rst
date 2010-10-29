1. Intro
==============

Firstly causal and its developers are not associated with any of the services we integrate with.

All integration is done using publicly available APIs. Where extra permission is required we ask the logged in user to 
provide us/causal with permission to access their data using the API supplied by the service owner.

WE DO NOT STORE ANY DATA FROM THE THIRD PARTY EXCEPT OAUTH TOKENS
We only store the oauth details, causal doesn't store any updates from the third party. Causal does cache
pages locally, these only survice as long as the server is running. Restarting the server should clear the cache.

It was deliberate choice not to store any data to avoid any potential privacy issues.

That said causal will store usernames and oauth permissions in the database. Causal uses the least
amounts of permissions required to get data from a third party. That said not every service has
fine grained permissions so please be aware that the oauth tokens should not be shared.

2. Design
==============

We have broken each service we integrate with in a Django application. Each service can enabled from local.settings.py like so:

INSTALLED_SERVICES = (
 - 'causal.twitter',
 - 'causal.foursquare',
 - #'causal.flickr',
 - #'causal.feed',
 - #'causal.facebook',
 - #'causal.github',
 - #'causal.lastfm',
 - #'causal.googlereader',
)

This enables only Foursqaure and Twitter services to the user to integrate with.

3. Run Modes
==============

Causal can be run as multi user service by enabling user registration in local.settings.py as so:

ENABLE_REGISTRATION = True

This will allow users to register with the site user the django-registration app. This will email the user after sign up with a link to validate their email address.

If multi user access isnt required as for example you wish to run you own causal instance just for your updates set ENABLE_REGISTRATION = False to disable user registration. You will then need to register a user by hand in the admin interface, locate at http://HOSTNAME:PORT/_ca-admin That is the default address of the admin interface.

4. Build/Install
==============

Currently the build for causal is configured in buildout. This is on going and should be finished soon.

In the mean time you will need to have the following installed for the core of the system:

 - Django - 1.2.3
 - oauth2 - 1.2.0
 - south - 0.7.1
 - django-registration - 0.7
 - jogging - 0.2.2 
 - django-timezones - 0.1.4
 - python-dateutil - 1.5
 - pytz 

The following allow the different services to be interacted with:

 - BeautifulSoup - 3.0.8.1  Required for github.com integration
 - feedparser - 4.1  Required for general rss parsing - google/com/reader
 - flickrapi - 1.4.2  Required to talk to flickr.com
 - github2 - 0.1.2  Required to talk to github.com
 - tweepy - 1.7.1  Required to talk to twitter.com
 - twitter-text-py - 1.0.3  Required to parse data back from twitter.com
 - pyfacegraph - 0.0.4  Required for facebook.com

5. Accessing Services
=====================

After enabling a service the user will be prompted either for a username for the basic services and oauth for restrictive ones.

5.1 Sharing
-----------

The service is shared using the sliders on the settings page. Once a service is shared its available as a json feed:

http://hostname.com/username.json

Where username is the username of the user.

5.2 Stats
-----------

The front page contains links to stats about each service. 

5.3 Enabling a service
----------------------

Add the service into INSTALLED_APPS. 

Next you need to add an oauth in the backand http://hostname.com/_ca-admin. Next you need to create a Service app 
linking to the oauth object.

The service is then ready to roll.

6. Upcoming
===========

We had our own ideas of where we wanted to lead the project but we decided its the users who know best. With this in mind we are open to suggestions for improvements and feature requests. Email us at team@causal.com or find the current ticket list at: http://github.com/causality/causal/issues

The project is hosted at http://github.com/causality please fork away!

7. Hacking
===========

7.1 Adding more services
------------------------
A service is django app. Create a basic app. The are a few key this to note.

7.1.1 urls.py
-------------

 - / : callback called by the third party usually on oauth callback
 - /auth : called when the user enables the service this typically sends the user off to the third party
 - /stats : adds a link on the home page

7.1.2 service.py
----------------

get_items
---------------

This is the key method that fetches the data and returns data in json for the interface to render.