# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Host.sync_dirs'
        db.add_column('syncmedia_host', 'sync_dirs',
                      self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Host.sync_dirs'
        db.delete_column('syncmedia_host', 'sync_dirs')


    models = {
        'syncmedia.host': {
            'Meta': {'object_name': 'Host'},
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '9922', 'max_length': '40'}),
            'pubkey': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'sync_dirs': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['syncmedia']