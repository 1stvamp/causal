# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'OAuthSetting'
        db.create_table('main_oauthsetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('consumer_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('consumer_secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('request_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('access_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('user_auth_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('callback_url_base', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('main', ['OAuthSetting'])

        # Adding model 'ServiceApp'
        db.create_table('main_serviceapp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('oauth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.OAuthSetting'], null=True, blank=True)),
        ))
        db.send_create_signal('main', ['ServiceApp'])

        # Adding model 'UserService'
        db.create_table('main_userservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ServiceApp'])),
            ('setup', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['UserService'])

        # Adding model 'RequestToken'
        db.create_table('main_requesttoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.UserService'], null=True, blank=True)),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('oauth_verify', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['RequestToken'])

        # Adding model 'AccessToken'
        db.create_table('main_accesstoken', (
            ('requesttoken_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.RequestToken'], unique=True, primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('api_token', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['AccessToken'])


    def backwards(self, orm):
        
        # Deleting model 'OAuthSetting'
        db.delete_table('main_oauthsetting')

        # Deleting model 'ServiceApp'
        db.delete_table('main_serviceapp')

        # Deleting model 'UserService'
        db.delete_table('main_userservice')

        # Deleting model 'RequestToken'
        db.delete_table('main_requesttoken')

        # Deleting model 'AccessToken'
        db.delete_table('main_accesstoken')


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
            'api_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'requesttoken_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.RequestToken']", 'unique': 'True', 'primary_key': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'main.oauthsetting': {
            'Meta': {'object_name': 'OAuthSetting'},
            'access_token_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'callback_url_base': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'consumer_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'consumer_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_token_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user_auth_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'main.requesttoken': {
            'Meta': {'object_name': 'RequestToken'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'oauth_verify': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.UserService']", 'null': 'True', 'blank': 'True'})
        },
        'main.serviceapp': {
            'Meta': {'object_name': 'ServiceApp'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'oauth': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.OAuthSetting']", 'null': 'True', 'blank': 'True'})
        },
        'main.userservice': {
            'Meta': {'object_name': 'UserService'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ServiceApp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setup': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['main']
