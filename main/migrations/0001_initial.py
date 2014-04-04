# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileStorage'
        db.create_table(u'main_filestorage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('blob', self.gf('django.db.models.fields.BinaryField')()),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('size', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'main', ['FileStorage'])


    def backwards(self, orm):
        # Deleting model 'FileStorage'
        db.delete_table(u'main_filestorage')


    models = {
        u'main.filestorage': {
            'Meta': {'object_name': 'FileStorage'},
            'blob': ('django.db.models.fields.BinaryField', [], {}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['main']