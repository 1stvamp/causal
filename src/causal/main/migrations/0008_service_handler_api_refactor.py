# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting model 'OAuthSetting'
        db.delete_table('main_oauthsetting')

        # Adding model 'OAuth'
        db.create_table('main_oauth', (
            ('baseauth_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.BaseAuth'], unique=True, primary_key=True)),
            ('request_token', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.RequestToken'], null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='main_oauth_related', null=True, to=orm['main.AccessToken'])),
        ))
        db.send_create_signal('main', ['OAuth'])

        # Adding model 'Auth'
        db.create_table('main_auth', (
            ('baseauth_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.BaseAuth'], unique=True, primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('main', ['Auth'])

        # Adding model 'BaseAuth'
        db.create_table('main_baseauth', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('main', ['BaseAuth'])

        # Deleting field 'RequestToken.service'
        db.delete_column('main_requesttoken', 'service_id')

        # Adding field 'UserService.auth_type'
        db.add_column('main_userservice', 'auth_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True), keep_default=False)

        # Adding field 'UserService.auth_object_id'
        db.add_column('main_userservice', 'auth_object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True), keep_default=False)

        # Deleting field 'AccessToken.username'
        db.delete_column('main_accesstoken', 'username')

        # Deleting field 'AccessToken.userid'
        db.delete_column('main_accesstoken', 'userid')

        # Deleting field 'AccessToken.api_token'
        db.delete_column('main_accesstoken', 'api_token')

        # Deleting field 'ServiceApp.oauth'
        db.delete_column('main_serviceapp', 'oauth_id')


    def backwards(self, orm):

        # Adding model 'OAuthSetting'
        db.create_table('main_oauthsetting', (
            ('callback_url_base', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('consumer_secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('request_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('consumer_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('access_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('user_auth_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('main', ['OAuthSetting'])

        # Deleting model 'OAuth'
        db.delete_table('main_oauth')

        # Deleting model 'Auth'
        db.delete_table('main_auth')

        # Deleting model 'BaseAuth'
        db.delete_table('main_baseauth')

        # Adding field 'RequestToken.service'
        db.add_column('main_requesttoken', 'service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.UserService'], null=True, blank=True), keep_default=False)

        # Deleting field 'UserService.auth_type'
        db.delete_column('main_userservice', 'auth_type_id')

        # Deleting field 'UserService.auth_object_id'
        db.delete_column('main_userservice', 'auth_object_id')

        # Adding field 'AccessToken.username'
        db.add_column('main_accesstoken', 'username', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'AccessToken.userid'
        db.add_column('main_accesstoken', 'userid', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'AccessToken.api_token'
        db.add_column('main_accesstoken', 'api_token', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'ServiceApp.oauth'
        db.add_column('main_serviceapp', 'oauth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.OAuthSetting'], null=True, blank=True), keep_default=False)


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
        'main.auth': {
            'Meta': {'object_name': 'Auth', '_ormbases': ['main.BaseAuth']},
            'baseauth_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.BaseAuth']", 'unique': 'True', 'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'main.baseauth': {
            'Meta': {'object_name': 'BaseAuth'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {})
        },
        'main.oauth': {
            'Meta': {'object_name': 'OAuth', '_ormbases': ['main.BaseAuth']},
            'access_token': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'main_oauth_related'", 'null': 'True', 'to': "orm['main.AccessToken']"}),
            'baseauth_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.BaseAuth']", 'unique': 'True', 'primary_key': 'True'}),
            'request_token': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.RequestToken']", 'null': 'True', 'blank': 'True'})
        },
        'main.requesttoken': {
            'Meta': {'object_name': 'RequestToken'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'oauth_verify': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'main.serviceapp': {
            'Meta': {'object_name': 'ServiceApp'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'main.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'default': "'Europe/London'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'main.userservice': {
            'Meta': {'object_name': 'UserService'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ServiceApp']"}),
            'auth_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'auth_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'setup': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'share': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['main']
