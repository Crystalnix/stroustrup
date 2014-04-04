# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Books_QR'
        db.delete_table(u'book_library_books_qr')

        # Deleting field 'Book.file'
        db.delete_column(u'book_library_book', 'file')

        # Adding field 'Book.qr_image'
        db.add_column(u'book_library_book', 'qr_image',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Book.book_file'
        db.add_column(u'book_library_book', 'book_file',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)


        # Changing field 'Book.title'
        db.alter_column(u'book_library_book', 'title', self.gf('django.db.models.fields.CharField')(max_length=75))
        # Adding field 'Book_Request.book_image_url'
        db.add_column(u'book_library_book_request', 'book_image_url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, null='', blank=True),
                      keep_default=False)

        # Adding field 'Book_Request.book_title'
        db.add_column(u'book_library_book_request', 'book_title',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Book_Request.book_authors'
        db.add_column(u'book_library_book_request', 'book_authors',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Book_Request.book_price'
        db.add_column(u'book_library_book_request', 'book_price',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Book_Request.book_description'
        db.add_column(u'book_library_book_request', 'book_description',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'Book_Request.title'
        db.alter_column(u'book_library_book_request', 'title', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):
        # Adding model 'Books_QR'
        db.create_table(u'book_library_books_qr', (
            ('qr', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['book_library.Book'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'book_library', ['Books_QR'])


        # User chose to not deal with backwards NULL issues for 'Book.file'
        raise RuntimeError("Cannot reverse this migration. 'Book.file' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Book.file'
        db.add_column(u'book_library_book', 'file',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True),
                      keep_default=False)

        # Deleting field 'Book.qr_image'
        db.delete_column(u'book_library_book', 'qr_image')

        # Deleting field 'Book.book_file'
        db.delete_column(u'book_library_book', 'book_file')


        # Changing field 'Book.title'
        db.alter_column(u'book_library_book', 'title', self.gf('django.db.models.fields.CharField')(max_length=45))
        # Deleting field 'Book_Request.book_image_url'
        db.delete_column(u'book_library_book_request', 'book_image_url')

        # Deleting field 'Book_Request.book_title'
        db.delete_column(u'book_library_book_request', 'book_title')

        # Deleting field 'Book_Request.book_authors'
        db.delete_column(u'book_library_book_request', 'book_authors')

        # Deleting field 'Book_Request.book_price'
        db.delete_column(u'book_library_book_request', 'book_price')

        # Deleting field 'Book_Request.book_description'
        db.delete_column(u'book_library_book_request', 'book_description')


        # Changing field 'Book_Request.title'
        db.alter_column(u'book_library_book_request', 'title', self.gf('django.db.models.fields.CharField')(max_length=30))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'book_library.author': {
            'Meta': {'object_name': 'Author'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'book_library.book': {
            'Meta': {'ordering': "['title']", 'object_name': 'Book'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'books'", 'symmetrical': 'False', 'to': u"orm['book_library.Author']"}),
            'book_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'book_rating': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['book_library.Book_Rating']", 'null': 'None', 'symmetrical': 'False', 'blank': 'True'}),
            'busy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'books'", 'blank': 'True', 'symmetrical': 'False', 'to': u"orm['book_library.Book_Comment']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'e_version_exists': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '13', 'blank': 'True'}),
            'paperback_version_exists': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'qr_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'books'", 'blank': 'True', 'to': u"orm['book_library.Book_Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'books'", 'blank': 'True', 'through': u"orm['book_library.Client_Story_Record']", 'to': u"orm['auth.User']"})
        },
        u'book_library.book_comment': {
            'Meta': {'object_name': 'Book_Comment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'comment'", 'blank': 'True', 'to': u"orm['auth.User']"})
        },
        u'book_library.book_rating': {
            'Meta': {'object_name': 'Book_Rating'},
            'common_rating': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_owner': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'rating'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'user_rating': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'votes': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'book_library.book_request': {
            'Meta': {'object_name': 'Book_Request'},
            'book_authors': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'book_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'book_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': "''", 'blank': 'True'}),
            'book_price': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'book_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': "''"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'request'", 'blank': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'book_library.book_tag': {
            'Meta': {'object_name': 'Book_Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'book_library.client_story_record': {
            'Meta': {'object_name': 'Client_Story_Record'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['book_library.Book']"}),
            'book_returned': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'book_taken': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'book_library.request_return': {
            'Meta': {'object_name': 'Request_Return'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['book_library.Book']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processing_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_request': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user_request': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['book_library']