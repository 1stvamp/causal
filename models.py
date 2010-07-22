from google.appengine.ext import db

class OAuthRequestToken(db.Model):
    """OAuth Request Token."""

    user = db.StringProperty()
    service = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class OAuthAccessToken(db.Model):
    """OAuth Access Token."""

    user = db.StringProperty()
    service = db.StringProperty()
    google_username = db.StringProperty()
    specifier = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)