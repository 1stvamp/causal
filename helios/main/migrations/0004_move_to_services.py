# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'OAuthAccessToken'
        db.delete_table('main_oauthaccesstoken')

        # Deleting model 'LastFMSettings'
        db.delete_table('main_lastfmsettings')

        # Deleting model 'OAuthRequestToken'
        db.delete_table('main_oauthrequesttoken')

        # Adding model 'RequestToken'
        db.create_table('main_requesttoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Service'], null=True, blank=True)),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('main', ['RequestToken'])

        # Adding model 'Service'
        db.create_table('main_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('oauth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.OAuthSetting'])),
            ('app_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('main', ['Service'])

        # Adding model 'AccessToken'
        db.create_table('main_accesstoken', (
            ('requesttoken_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.RequestToken'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('main', ['AccessToken'])

        # Adding model 'OAuthSetting'
        db.create_table('main_oauthsetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('consumer_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('consumer_secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('request_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('access_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('user_auth_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('default_api_prefix', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('default_api_suffix', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('main', ['OAuthSetting'])


    def backwards(self, orm):
        
        # Adding model 'OAuthAccessToken'
        db.create_table('main_oauthaccesstoken', (
            ('service', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('main', ['OAuthAccessToken'])

        # Adding model 'LastFMSettings'
        db.create_table('main_lastfmsettings', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('main', ['LastFMSettings'])

        # Adding model 'OAuthRequestToken'
        db.create_table('main_oauthrequesttoken', (
            ('service', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('main', ['OAuthRequestToken'])

        # Deleting model 'RequestToken'
        db.delete_table('main_requesttoken')

        # Deleting model 'Service'
        db.delete_table('main_service')

        # Deleting model 'AccessToken'
        db.delete_table('main_accesstoken')

        # Deleting model 'OAuthSetting'
        db.delete_table('main_oauthsetting')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.accesstoken': {
            'Meta': {'object_name': 'AccessToken', '_ormbases': ['main.RequestToken']},
            'requesttoken_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.RequestToken']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.oauthsetting': {
            'Meta': {'object_name': 'OAuthSetting'},
            'access_token_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'consumer_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'consumer_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'default_api_prefix': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'default_api_suffix': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_token_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user_auth_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'main.requesttoken': {
            'Meta': {'object_name': 'RequestToken'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Service']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'main.service': {
            'Meta': {'object_name': 'Service'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'oauth': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.OAuthSetting']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['main']
