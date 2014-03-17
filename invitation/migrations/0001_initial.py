# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Invite'
        db.create_table(u'invitation_invite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=75, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=75, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('is_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('who_invite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profile.Library'], null=True, blank=True)),
            ('date_requested', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_used', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'invitation', ['Invite'])


    def backwards(self, orm):
        # Deleting model 'Invite'
        db.delete_table(u'invitation_invite')


    models = {
        u'invitation.invite': {
            'Meta': {'object_name': 'Invite'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_requested': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_used': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'who_invite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profile.Library']", 'null': 'True', 'blank': 'True'})
        },
        u'profile.library': {
            'Meta': {'object_name': 'Library'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['invitation']